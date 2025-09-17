import os
import re
from pathlib import Path
from shutil import copy
from typing import Union, List, Set
import frontmatter


class PartialCopy:
    """
    Handles partial copying of files with dependency tracking and content modification.
    """

    @staticmethod
    def partial_copy(
        source: Union[str, Path, List[Union[str, Path]]],
        root: Union[str, Path],
        destination: Union[str, Path],
    ) -> None:
        """
        Copies files, a list of files,
        or files matching a glob pattern to the specified folder.
        Creates all necessary directories if they don't exist.
        """

        if isinstance(source, list):
            source_display = "\n- " + "\n- ".join([str(item) for item in source])
        else:
            source_display = str(source)

        print(f"Partial build is processing...\nList of files: {source_display}")

        destination_path = Path(destination)
        root_path = Path(root)
        image_extensions = {'.jpg', '.jpeg', '.png', '.svg', '.gif', '.bmp', '.webp'}
        image_pattern = re.compile(
            r'!\[.*?\]\((.*?)\)|<img.*?src=["\'](.*?)["\']', 
            re.IGNORECASE
        )
        include_statement_pattern = re.compile(
            r'(?<!\<)\<(?:include)(\s*(src=\")(?P<src>.*?)(\")|)'
            r'(?:\s[^\<\>]*)?\>(?P<path>.*?)\<\/(?:include)\>',
            flags=re.DOTALL
        )

        copied_files_count = 0
        processed_files = set()
        max_recursion_depth = 10

        def _modify_markdown_file( # pylint: disable=too-many-arguments
            file_path: Union[str, Path],
            dst_file_path: Union[str, Path],
            not_build: bool = True,
            remove_content: bool = True,
            keep_first_header: bool = True,
            create_frontmatter: bool = True,
            dry_run: bool = False,
        ):
            """Modify a Markdown file's frontmatter and content."""
            try:
                file_path = Path(file_path)
                content = file_path.read_text(encoding='utf-8')
                post = frontmatter.loads(content)
                changes_made = False

                # Process modifications
                changes_made = PartialCopy._process_frontmatter(post, not_build) or changes_made
                changes_made = PartialCopy._process_content(
                    post, remove_content, keep_first_header
                ) or changes_made

                if not PartialCopy._has_frontmatter(post) and create_frontmatter and (
                    not_build is not None or changes_made
                ):
                    changes_made = True

                if not changes_made:
                    return False, content

                output = PartialCopy._serialize_output(post, create_frontmatter)

                if dry_run:
                    return True, output

                dst_file_path.write_text(output, encoding='utf-8')
                return True, output

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error processing {file_path}: {str(e)}")
                return False, content

        def _find_referenced_images(file_path: Path) -> Set[Path]:
            """Finds all image files referenced in the given file."""
            image_paths = set()
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                for match in image_pattern.findall(content):
                    for group in match:
                        if group:
                            image_path = Path(file_path).parent / Path(group)
                            if image_path.suffix.lower() in image_extensions:
                                image_paths.add(image_path)
            return image_paths

        def _copy_files_without_content(src_dir: str, dst_dir: str):
            """Copies files, leaving only the first-level header."""
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            for file_root, _, files in os.walk(src_dir):
                for file_name in files:
                    src_file_path = os.path.join(file_root, file_name)
                    dirs = os.path.relpath(file_root, src_dir)
                    dst_file_path = Path(os.path.join(dst_dir, dirs, file_name))
                    dst_file_path.parent.mkdir(parents=True, exist_ok=True)
                    if file_name.endswith('.md'):
                        _modify_markdown_file(src_file_path, dst_file_path)

        def _prepare_paths_list(file_path, relative_path_root) -> List:
            include_paths = []
            match_includes = re.finditer(include_statement_pattern,
                                        file_path.read_text(encoding='utf-8'))
            for path in match_includes:
                paths_list = []
                groups = path.groupdict()
                if groups["path"]:
                    paths_list.append(groups["path"])
                if groups["src"]:
                    paths_list.append(groups["src"])

                for p in paths_list:
                    _path = Path(p)
                    if isinstance(file_path, Path):
                        rel_path = file_path.parent / _path
                        if rel_path.exists():
                            _path = rel_path
                    if not _path.exists():
                        _path = relative_path_root / _path
                    if _path.exists():
                        include_paths.append(_path)
            return include_paths

        def _copy_files_recursive(files_to_copy: List, recursion_level: int = 0):  # pylint: disable=too-many-branches
            """Recursively copies files and their dependencies."""
            nonlocal copied_files_count

            if recursion_level > max_recursion_depth:
                print(f"Warning: Maximum recursion depth ({max_recursion_depth}) exceeded")
                return

            referenced_images = set()

            for file_path in files_to_copy:
                file_path = Path(file_path)

                # Check if this file was already processed
                if file_path in processed_files:
                    continue
                processed_files.add(file_path)

                if not file_path.exists():
                    print(f"Warning: File {file_path} does not exist, skipping")
                    continue

                if file_path.is_relative_to(root_path):
                    relative_path = file_path.relative_to(root_path)
                    destination_file_path = destination_path / relative_path
                    destination_file_path.parent.mkdir(parents=True, exist_ok=True)

                    if file_path.exists():
                        # Find and copy includes
                        include_paths = _prepare_paths_list(file_path, root_path)
                        _copy_files_recursive(include_paths, recursion_level + 1)

                        # Find referenced images
                        referenced_images.update(_find_referenced_images(file_path))

                    # Copy the file
                    try:
                        copy(file_path, destination_file_path)
                        copied_files_count += 1
                    except FileNotFoundError as e:
                        print(f"File not found: {e}")
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"Error copying {file_path}: {e}")

            # Copy referenced images
            for image_path in referenced_images:
                image_path = Path(image_path)
                if image_path in processed_files:
                    continue
                processed_files.add(image_path)

                if image_path.exists():
                    if image_path.is_relative_to(root_path):
                        src_image_path = image_path.relative_to(root_path)
                    else:
                        src_image_path = image_path

                    dst_image_path = destination_path / src_image_path
                    dst_image_path.parent.mkdir(parents=True, exist_ok=True)

                    if image_path != dst_image_path:
                        try:
                            copy(image_path, dst_image_path)
                            copied_files_count += 1
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            print(f"Error copying image {image_path}: {e}")

        # Main logic with verification
        try:
            # Normalize source to file list
            if isinstance(source, (str, Path)):
                source_path = Path(source)
                if source_path.is_dir():
                    files_to_copy = list(source_path.rglob('*'))
                elif '*' in str(source_path):
                    # Handle glob pattern
                    files_to_copy = list(root_path.glob(str(source_path)))
                else:
                    files_to_copy = [source_path]
            else:
                files_to_copy = [Path(f) for f in source]

            print(f"Total files to process: {len(files_to_copy)}")

            # Copy files
            _copy_files_without_content(root_path, destination_path)
            _copy_files_recursive(files_to_copy)

            if copied_files_count == 0:
                print("Warning: No files were copied!")
            elif copied_files_count < len(files_to_copy):
                print(f"Warning: Only {copied_files_count} out of {len(files_to_copy)} files were copied") # pylint: disable=line-too-long

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error during copy operation: {e}")
            raise

    @staticmethod
    def _process_frontmatter(post, not_build: bool) -> bool:
        """Process frontmatter modifications."""
        if not_build is not None and post.get('not_build') != not_build:
            post['not_build'] = not_build
            return True
        return False

    @staticmethod
    def _process_content(post, remove_content: bool, keep_first_header: bool) -> bool:
        """Process content modifications."""
        if remove_content and post.content.strip():
            new_content = PartialCopy._extract_first_header(
                post.content) if keep_first_header else ''
            if post.content != new_content:
                post.content = new_content
                return True
        return False

    @staticmethod
    def _extract_first_header(content: str) -> str:
        """Extract first H1 header from content."""
        h1_match = re.search(r'^#\s+.+$', content, flags=re.MULTILINE)
        return h1_match.group(0) + '\n' if h1_match else ''

    @staticmethod
    def _serialize_output(post, create_frontmatter: bool) -> str:
        """Serialize post to text with proper formatting."""
        output = frontmatter.dumps(post)
        if not PartialCopy._has_frontmatter(post) and create_frontmatter:
            output = f"---\n{output}"
        return output + '\n'

    @staticmethod
    def _has_frontmatter(post: frontmatter.Post) -> bool:
        """Check if post has existing frontmatter."""
        return hasattr(post, 'metadata') and (post.metadata or hasattr(post, 'fm'))
