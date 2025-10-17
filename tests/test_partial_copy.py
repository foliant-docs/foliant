import frontmatter

from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory
from foliant.partial_copy import PartialCopy
from foliant.cli.make import Cli


class TestPartialCopy(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = TemporaryDirectory()
        self.source_dir = Path(self.test_dir.name) / "source"
        self.destination_dir = Path(self.test_dir.name) / "destination"
        self.source_dir.mkdir()
        self.destination_dir.mkdir()

        # Create some test files
        (self.source_dir / "file1.txt").write_text("Hello, file1!")
        (self.source_dir / "file2.txt").write_text("Hello, file2!")
        (self.source_dir / "subfolder").mkdir()
        (self.source_dir / "subfolder" / "file3.txt").write_text("Hello, file3!")
        (self.source_dir / "file2.md").write_text("# Header\nSome content")
        (self.source_dir / "subfolder" / "file3.md").write_text("# Another Header\nMore content")
        (self.source_dir / "file4.md").write_text("---\nkey: value\n---\n# Header\nSome content")

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_copy_single_file(self):
        # Test copying a single file
        source_file = self.source_dir / "file1.txt"
        PartialCopy.partial_copy(source_file, self.source_dir, self.destination_dir)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertEqual((self.destination_dir / "file1.txt").read_text(), "Hello, file1!")

    def test_copy_list_of_files(self):
        # Test copying a list of files
        source_files = [
            self.source_dir / "file1.txt",
            self.source_dir / "file2.txt"
        ]

        PartialCopy.partial_copy(source_files, self.source_dir, self.destination_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())

    def test_copy_list_of_files_two(self):
        # Test copying a list of files
        source_files = [
            str(self.source_dir / "file1.txt"),
            str(self.source_dir / "file2.md")
        ]
        PartialCopy.partial_copy(source_files, self.source_dir, self.destination_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.md").exists())

    def test_copy_glob_pattern(self):
        # Test copying files matching a glob pattern
        glob_pattern = str(self.source_dir / "*.txt")
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        PartialCopy.partial_copy(glob_pattern, self.source_dir, self.destination_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())
        self.assertFalse((self.destination_dir / "file3.txt").exists())  # file3 is in a subfolder

    def test_copy_glob_pattern_md(self):
        # Test copying files matching a glob pattern
        glob_pattern = str(self.source_dir / '*2.md')
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        PartialCopy.partial_copy(glob_pattern, self.source_dir, self.destination_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file2.md").exists())
        # Markdown files should be processed (content removed, frontmatter added)
        content = (self.destination_dir / "file2.md").read_text()
        self.assertIn("# Header\nSome content", content)

    def test_copy_glob_pattern_recursive(self):
        # Test copying files matching a recursive glob pattern
        glob_pattern = str(self.source_dir / "**" / "*.txt")
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        PartialCopy.partial_copy(glob_pattern, self.source_dir, self.destination_dir)

        # Check if the files were copied, including the one in the subfolder
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())
        self.assertTrue((self.destination_dir / "subfolder" / "file3.txt").exists())

    def test_copy_directory_structure(self):
        # Test copying a file while preserving directory structure
        source_file = self.source_dir / "subfolder" / "file3.txt"
        PartialCopy.partial_copy(source_file, self.source_dir, self.destination_dir)

        # Check if the file was copied with the directory structure
        self.assertTrue((self.destination_dir / "subfolder" / "file3.txt").exists())

    def test_copy_nonexistent_file(self):
        # Test copying a nonexistent file (should not raise error, just warn)
        source_file = self.source_dir / "nonexistent.txt"
        try:
            PartialCopy.partial_copy(source_file, self.source_dir, self.destination_dir)
            # Should not raise error, just print warning
        except Exception as e:
            self.fail(f"partial_copy raised unexpected exception: {e}")

    def test_copy_nonexistent_glob(self):
        # Test copying with a glob pattern that matches no files
        glob_pattern = str(self.source_dir / "*_suffix.md")
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        try:
            PartialCopy.partial_copy(glob_pattern, self.source_dir, self.destination_dir)
            # Should not raise error for empty glob results
        except Exception as e:
            self.fail(f"partial_copy raised unexpected exception: {e}")

    def test_copy_to_nonexistent_destination(self):
        # Test copying to a nonexistent destination (should create the destination folder)
        new_destination = self.destination_dir / "new_folder"
        PartialCopy.partial_copy(self.source_dir / "file1.txt", self.source_dir, new_destination)

        # Check if the file was copied and the destination folder was created
        self.assertTrue(new_destination.exists())
        self.assertTrue((new_destination / "file1.txt").exists())

    def test_copy_path_object(self):
        # Test copying using Path objects
        source_file = self.source_dir / "file1.txt"
        PartialCopy.partial_copy(source_file, self.source_dir, self.destination_dir)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())

    def test_copy_text_file(self):
        # Test copying a text file
        PartialCopy.partial_copy(str(self.source_dir / "file1.txt"), self.source_dir, self.destination_dir)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertEqual((self.destination_dir / "file1.txt").read_text(), "Hello, file1!")

    def test_copy_markdown_file(self):
        # Test copying a Markdown file
        PartialCopy.partial_copy(str(self.source_dir / "file2.md"), self.source_dir, self.destination_dir)

        # Check if the file was copied with frontmatter
        self.assertTrue((self.destination_dir / "file2.md").exists())
        content = (self.destination_dir / "file2.md").read_text()
        self.assertIn("# Header\nSome content", content)

    def test_copy_directory_structure_with_header(self):
        # Test copying a file while preserving directory structure
        PartialCopy.partial_copy(
            str(self.source_dir / "subfolder" / "file3.md"),
            self.source_dir,
            self.destination_dir
        )

        # Check if the file was copied with the directory structure
        self.assertTrue((self.destination_dir / "subfolder" / "file3.md").exists())
        content = (self.destination_dir / "subfolder" / "file3.md").read_text()
        self.assertIn("# Another Header\nMore content", content)

    def test_copy_referenced_images(self):
        # Create a Markdown file with image references
        md_content = "# Header\n![Image 1](images/image1.png)\n![Image 2](images/image2.jpg)"
        (self.source_dir / "file1.md").write_text(md_content)

        # Create referenced images
        (self.source_dir / "images").mkdir()
        (self.source_dir / "images" / "image1.png").write_text("Fake PNG content")
        (self.source_dir / "images" / "image2.jpg").write_text("Fake JPG content")

        # Copy files
        PartialCopy.partial_copy(str(self.source_dir / "file1.md"), self.source_dir, self.destination_dir)

        # Check if the Markdown file was copied
        self.assertTrue((self.destination_dir / "file1.md").exists())

        # Check if referenced images were copied
        self.assertTrue((self.destination_dir / "images" / "image1.png").exists())
        self.assertTrue((self.destination_dir / "images" / "image2.jpg").exists())

    def test_copy_referenced_images_with_annotation(self):
        # Create a Markdown file with image references
        md_content = "# Header\n![Image 1](images/image1.png \"annotation\")\n![Image 2](images/image2.jpg)"
        (self.source_dir / "file1.md").write_text(md_content)

        # Create referenced images
        (self.source_dir / "images").mkdir()
        (self.source_dir / "images" / "image1.png").write_text("Fake PNG content")
        (self.source_dir / "images" / "image2.jpg").write_text("Fake JPG content")

        # Copy files
        PartialCopy.partial_copy(str(self.source_dir / "file1.md"), self.source_dir, self.destination_dir)

        # Check if the Markdown file was copied
        self.assertTrue((self.destination_dir / "file1.md").exists())

        # Check if referenced images were copied
        self.assertTrue((self.destination_dir / "images" / "image1.png").exists())
        self.assertTrue((self.destination_dir / "images" / "image2.jpg").exists())

    def test_copy_with_string_paths(self):
        # Test copying with string paths instead of Path objects
        source_path = str(self.source_dir / "file1.txt")
        root_path = str(self.source_dir)
        dest_path = str(self.destination_dir)

        PartialCopy.partial_copy(source_path, root_path, dest_path)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())

    def test_copy_empty_list(self):
        # Test copying an empty list of files
        try:
            PartialCopy.partial_copy([], self.source_dir, self.destination_dir)
            # Should not raise error for empty list
        except Exception as e:
            self.fail(f"partial_copy raised unexpected exception for empty list: {e}")

    def test_has_frontmatter_method(self):
        content = (self.source_dir / "file4.md").read_text()
        post = frontmatter.loads(content)
        self.assertTrue(PartialCopy._has_frontmatter(post))

        # Test without metadata
        content = (self.source_dir / "file2.md").read_text()
        post = frontmatter.loads(content)
        self.assertFalse(PartialCopy._has_frontmatter(post))


if __name__ == '__main__':
    import unittest
    unittest.main()
