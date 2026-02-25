from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory

from foliant.backends.base import BaseBackend
from foliant.cli.make import Cli

class TestBackendCopyFiles(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = TemporaryDirectory()
        self.source_dir = Path(self.test_dir.name) / "source"
        self.destination_dir = Path(self.test_dir.name) / "destination"
        self.working_dir = self.destination_dir
        self.source_dir.mkdir()
        self.destination_dir.mkdir()

        # Create some test files
        (self.source_dir / "file1.txt").write_text("Hello, file1!")
        (self.source_dir / "file2.txt").write_text("Hello, file2!")
        (self.source_dir / "subfolder").mkdir()
        (self.source_dir / "subfolder" / "file3.txt").write_text("Hello, file3!")
        (self.source_dir / "file2.md").write_text("# Header\nSome content")
        (self.source_dir / "subfolder" / "file3.md").write_text("# Another Header\nMore content")

    def tearDtown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_copy_single_file(self):
        # Test copying a single file
        source_file = self.source_dir / "file1.txt"
        source_file = Cli.prepare_list_of_file(source_file, self.destination_dir)
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertEqual((self.destination_dir / "file1.txt").read_text(), "Hello, file1!")

    def test_copy_list_of_files(self):
        # Test copying a list of files
        source_files = [
            self.source_dir / "file1.txt",
            self.source_dir / "file2.txt"
        ]

        source_files = Cli.prepare_list_of_file(source_files, self.destination_dir)
        BaseBackend.partial_copy(source_files, self.source_dir, self.working_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())


    def test_copy_list_of_files_two(self):
        # Test copying a list of files
        source_files = [
            str(self.source_dir / "file1.txt"),
            str(self.source_dir / "file2.md")
        ]
        source_files = Cli.prepare_list_of_file(source_files, self.destination_dir)
        BaseBackend.partial_copy(source_files, self.source_dir, self.working_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.md").exists())

    def test_copy_glob_pattern(self):
        # Test copying files matching a glob pattern
        glob_pattern = str(self.source_dir / "*.txt")
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        BaseBackend.partial_copy(glob_pattern, self.source_dir, self.working_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())
        self.assertFalse((self.destination_dir / "file3.txt").exists())  # file3 is in a subfolder

    def test_copy_glob_pattern_md(self):
        # Test copying files matching a glob pattern
        glob_pattern = str(self.source_dir / '*2.md')
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        BaseBackend.partial_copy(glob_pattern, self.source_dir, self.working_dir)

        # Check if the files were copied
        self.assertTrue((self.destination_dir / "file2.md").exists())
        self.assertEqual((self.destination_dir / "file2.md").read_text(), "# Header\nSome content")
        self.assertTrue((self.destination_dir / "subfolder" / "file3.md").exists())
        self.assertEqual((self.destination_dir / "subfolder" / "file3.md").read_text(), "---\nnot_build: true\n---\n\n# Another Header\n") # Only '*2.md' files should be copied with content

    def test_copy_glob_pattern_recursive(self):
        # Test copying files matching a recursive glob pattern
        glob_pattern = str(self.source_dir / "**" / "*.txt")
        glob_pattern = Cli.prepare_list_of_file(glob_pattern, self.destination_dir)
        BaseBackend.partial_copy(glob_pattern, self.source_dir, self.working_dir)

        # Check if the files were copied, including the one in the subfolder
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertTrue((self.destination_dir / "file2.txt").exists())
        self.assertTrue((self.destination_dir / "subfolder" / "file3.txt").exists())

    def test_copy_directory_structure(self):
        # Test copying a file while preserving directory structure
        source_file = self.source_dir / "subfolder" / "file3.txt"
        source_file = Cli.prepare_list_of_file(source_file, self.destination_dir)
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the file was copied with the directory structure
        self.assertTrue((self.destination_dir / "subfolder" / "file3.txt").exists())

    # def test_copy_nonexistent_file(self):
    #     # Test copying a nonexistent file (should raise FileNotFoundError)
    #     source_file = self.source_dir / "nonexistent.txt"
    #     with self.assertRaises(FileNotFoundError):
    #         BaseBackend.partial_copy(source_file,  self.source_dir, self.working_dir)

    # def test_copy_nonexistent_glob(self):
    #     # Test copying with a glob pattern that matches no files
    #     glob_pattern = str(self.source_dir / "*_suffix.md")
    #     BaseBackend.partial_copy(glob_pattern,  self.source_dir, self.working_dir)

    #     # Check that no files were copied
    #     self.assertTrue((self.destination_dir / "file2.md").exists())
    #     self.assertEqual((self.destination_dir / "file2.md").read_text(), "# Header\n")
    #     self.assertTrue((self.destination_dir / "subfolder" / "file3.md").exists())
    #     self.assertEqual((self.destination_dir / "subfolder" / "file3.md").read_text(), "# Another Header\n")

    # def test_copy_to_nonexistent_destination(self):
    #     # Test copying to a nonexistent destination (should create the destination folder)
    #     new_destination = self.destination_dir / "new_folder"
    #     BaseBackend.partial_copy(self.source_dir / "file1.txt", new_destination, self.source_dir, self.working_dir)

    #     # Check if the file was copied and the destination folder was created
    #     self.assertTrue(new_destination.exists())
    #     self.assertTrue((new_destination / "file1.txt").exists())

    def test_copy_path_object(self):
        # Test copying using Path objects
        source_file = self.source_dir / "file1.txt"
        destination = self.destination_dir / "file1.txt"
        source_file = Cli.prepare_list_of_file(source_file, destination)
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the file was copied
        self.assertTrue(destination.exists())

    def test_copy_text_file(self):
        source_file = Cli.prepare_list_of_file(str(self.source_dir / "file1.txt"), self.destination_dir)
        # Test copying a text file
        source_file = Cli.prepare_list_of_file(str(self.source_dir / "file1.txt"), self.destination_dir)
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the file was copied
        self.assertTrue((self.destination_dir / "file1.txt").exists())
        self.assertEqual((self.destination_dir / "file1.txt").read_text(), "Hello, file1!")

    def test_copy_markdown_file(self):
        source_file = Cli.prepare_list_of_file(str(self.source_dir / "file2.md"), self.destination_dir)
        # Test copying a Markdown file
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if only the header was copied
        self.assertTrue((self.destination_dir / "file2.md").exists())
        self.assertEqual((self.destination_dir / "file2.md").read_text(), "# Header\nSome content")

    def test_copy_directory_structure_with_header(self):
        source_file = Cli.prepare_list_of_file(str(self.source_dir / "subfolder" / "file3.md"), self.destination_dir)
        # Test copying a file while preserving directory structure
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the file was copied with the directory structure
        self.assertTrue((self.destination_dir / "subfolder" / "file3.md").exists())
        self.assertEqual((self.destination_dir / "subfolder" / "file3.md").read_text(), "# Another Header\nMore content")

    def test_copy_referenced_images(self):
        # Create a Markdown file with image references
        md_content = "# Header\n![Image 1](images/image1.png)\n![Image 2](images/image2.jpg)"
        (self.source_dir / "file1.md").write_text(md_content)

        # Create referenced images
        (self.source_dir / "images").mkdir()
        (self.source_dir / "images" / "image1.png").write_text("Fake PNG content")
        (self.source_dir / "images" / "image2.jpg").write_text("Fake JPG content")

        source_file = Cli.prepare_list_of_file(str(self.source_dir / "file1.md"), self.destination_dir)

        # Copy files
        BaseBackend.partial_copy(source_file, self.source_dir, self.working_dir)

        # Check if the Markdown file was copied
        self.assertTrue((self.destination_dir / "file1.md").exists())

        # Check if referenced images were copied
        self.assertTrue((self.destination_dir / "images" / "image1.png").exists())
        self.assertTrue((self.destination_dir / "images" / "image2.jpg").exists())
