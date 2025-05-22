import unittest
import os
import uuid
import json
from notes_app import Note, NotesManager

class TestNotesManager(unittest.TestCase):

    def setUp(self):
        """Set up a new NotesManager and a test file for each test."""
        self.test_file = f"test_notes_{uuid.uuid4().hex}.json"
        self.manager = NotesManager(filename=self.test_file)

    def tearDown(self):
        """Clean up the test file after each test."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_create_note(self):
        self.assertEqual(len(self.manager.notes), 0)
        note1 = self.manager.create_note("Test Title 1", "Test Content 1")
        self.assertEqual(len(self.manager.notes), 1)
        self.assertIsInstance(note1, Note)
        self.assertEqual(note1.title, "Test Title 1")
        self.assertEqual(note1.content, "Test Content 1")
        self.assertEqual(note1.color, "white") # Default color

        note2 = self.manager.create_note("Test Title 2", "Test Content 2", "blue")
        self.assertEqual(len(self.manager.notes), 2)
        self.assertEqual(note2.title, "Test Title 2")
        self.assertEqual(note2.content, "Test Content 2")
        self.assertEqual(note2.color, "blue")
        self.assertNotEqual(note1.id, note2.id)

    def test_edit_note(self):
        note = self.manager.create_note("Original Title", "Original Content", "red")
        note_id_str = str(note.id)

        # Edit title
        self.assertTrue(self.manager.edit_note(note_id_str, title="New Title"))
        self.assertEqual(self.manager.notes[0].title, "New Title")
        self.assertEqual(self.manager.notes[0].content, "Original Content") # Content should remain
        self.assertEqual(self.manager.notes[0].color, "red") # Color should remain

        # Edit content
        self.assertTrue(self.manager.edit_note(note_id_str, content="New Content"))
        self.assertEqual(self.manager.notes[0].title, "New Title") # Title should remain
        self.assertEqual(self.manager.notes[0].content, "New Content")
        self.assertEqual(self.manager.notes[0].color, "red") # Color should remain

        # Edit color
        self.assertTrue(self.manager.edit_note(note_id_str, color="green"))
        self.assertEqual(self.manager.notes[0].title, "New Title")
        self.assertEqual(self.manager.notes[0].content, "New Content")
        self.assertEqual(self.manager.notes[0].color, "green")

        # Edit multiple attributes
        self.assertTrue(self.manager.edit_note(note_id_str, title="Final Title", content="Final Content", color="yellow"))
        self.assertEqual(self.manager.notes[0].title, "Final Title")
        self.assertEqual(self.manager.notes[0].content, "Final Content")
        self.assertEqual(self.manager.notes[0].color, "yellow")

        # Attempt to edit a non-existent note
        non_existent_id = uuid.uuid4().hex
        self.assertFalse(self.manager.edit_note(non_existent_id, title="Won't Work"))
        
        # Ensure no other note was accidentally edited
        self.assertEqual(self.manager.notes[0].title, "Final Title")


    def test_delete_note(self):
        note1 = self.manager.create_note("To Delete", "Content")
        note2 = self.manager.create_note("To Keep", "Content")
        self.assertEqual(len(self.manager.notes), 2)

        note1_id_str = str(note1.id)
        self.assertTrue(self.manager.delete_note(note1_id_str))
        self.assertEqual(len(self.manager.notes), 1)
        self.assertEqual(self.manager.notes[0].title, "To Keep") # Check remaining note

        # Attempt to delete already deleted note
        self.assertFalse(self.manager.delete_note(note1_id_str))
        self.assertEqual(len(self.manager.notes), 1) # Count should remain 1

        # Attempt to delete a non-existent note
        non_existent_id = uuid.uuid4().hex
        self.assertFalse(self.manager.delete_note(non_existent_id))
        self.assertEqual(len(self.manager.notes), 1)

    def test_search_notes(self):
        self.manager.create_note("Alpha Task", "Important project details", "red")
        self.manager.create_note("Beta Plan", "Another task with details", "blue")
        self.manager.create_note("Gamma Project", "Review alpha version", "green")

        # Search by title (case-insensitive)
        results_alpha = self.manager.search_notes("alpha")
        self.assertEqual(len(results_alpha), 2) # "Alpha Task", "Gamma Project" (due to "alpha" in content)
        self.assertTrue(any(n.title == "Alpha Task" for n in results_alpha))
        self.assertTrue(any(n.title == "Gamma Project" for n in results_alpha))


        results_project = self.manager.search_notes("PROJECT") # Uppercase
        self.assertEqual(len(results_project), 2) # "Alpha Task", "Gamma Project"
        self.assertTrue(any(n.title == "Alpha Task" for n in results_project))
        self.assertTrue(any(n.title == "Gamma Project" for n in results_project))


        # Search by content (case-insensitive)
        results_details = self.manager.search_notes("DETAILS")
        self.assertEqual(len(results_details), 2) # "Alpha Task", "Beta Plan"
        self.assertTrue(any(n.title == "Alpha Task" for n in results_details))
        self.assertTrue(any(n.title == "Beta Plan" for n in results_details))

        # Search with keyword matching multiple notes
        results_task = self.manager.search_notes("task")
        self.assertEqual(len(results_task), 2) # "Alpha Task", "Beta Plan"

        # Search with keyword that matches no notes
        results_none = self.manager.search_notes("xyz_non_existent_zyx")
        self.assertEqual(len(results_none), 0)

        # Search in empty notes list
        self.manager.delete_note(str(self.manager.notes[0].id))
        self.manager.delete_note(str(self.manager.notes[0].id))
        self.manager.delete_note(str(self.manager.notes[0].id))
        self.assertEqual(len(self.manager.notes), 0)
        results_empty = self.manager.search_notes("anything")
        self.assertEqual(len(results_empty), 0)

    def test_persistence_create_load(self):
        note1_orig = self.manager.create_note("Persistent Note 1", "Content 1", "yellow")
        note2_orig = self.manager.create_note("Persistent Note 2", "Content 2", "purple")
        
        # Create a new manager instance with the same file
        manager2 = NotesManager(filename=self.test_file)
        self.assertEqual(len(manager2.notes), 2)

        loaded_note1 = manager2.search_notes("Persistent Note 1")[0]
        loaded_note2 = manager2.search_notes("Persistent Note 2")[0]

        self.assertEqual(loaded_note1.id, note1_orig.id)
        self.assertEqual(loaded_note1.title, note1_orig.title)
        self.assertEqual(loaded_note1.content, note1_orig.content)
        self.assertEqual(loaded_note1.color, note1_orig.color)

        self.assertEqual(loaded_note2.id, note2_orig.id)
        self.assertEqual(loaded_note2.title, note2_orig.title)
        self.assertEqual(loaded_note2.content, note2_orig.content)
        self.assertEqual(loaded_note2.color, note2_orig.color)

    def test_persistence_edit_delete_load(self):
        note1 = self.manager.create_note("Initial Edit", "Initial Content", "blue")
        note2 = self.manager.create_note("To Be Deleted", "Delete Me", "red")
        note1_id_str = str(note1.id)
        note2_id_str = str(note2.id)

        # Edit note1
        self.manager.edit_note(note1_id_str, title="Updated Title", color="green")
        # Delete note2
        self.manager.delete_note(note2_id_str)

        # Create a new manager instance to load from the file
        manager2 = NotesManager(filename=self.test_file)
        self.assertEqual(len(manager2.notes), 1) # note2 should be gone

        loaded_note1 = manager2.notes[0]
        self.assertEqual(loaded_note1.id, note1_id_str)
        self.assertEqual(loaded_note1.title, "Updated Title")
        self.assertEqual(loaded_note1.content, "Initial Content") # Content was not edited
        self.assertEqual(loaded_note1.color, "green")

        # Ensure the deleted note is not present
        search_deleted = manager2.search_notes("To Be Deleted")
        self.assertEqual(len(search_deleted), 0)

    def test_load_from_non_existent_file(self):
        # setUp creates self.manager with self.test_file, which won't exist
        # until a note is created and saved.
        # This test ensures that loading from a non-existent file
        # results in an empty notes list without errors.
        fresh_manager = NotesManager(filename="non_existent_file_for_sure.json")
        self.assertEqual(len(fresh_manager.notes), 0)
        # Clean up if a file was accidentally created (should not happen here)
        if os.path.exists("non_existent_file_for_sure.json"):
            os.remove("non_existent_file_for_sure.json")

    def test_load_from_empty_or_invalid_json_file(self):
        # Test with an empty file
        empty_file = f"empty_test_notes_{uuid.uuid4().hex}.json"
        with open(empty_file, 'w') as f:
            f.write("") # Empty file
        
        manager_empty = NotesManager(filename=empty_file)
        self.assertEqual(len(manager_empty.notes), 0)
        os.remove(empty_file)

        # Test with an invalid JSON file
        invalid_json_file = f"invalid_json_test_notes_{uuid.uuid4().hex}.json"
        with open(invalid_json_file, 'w') as f:
            f.write("{not_a_valid_json_")
        
        manager_invalid = NotesManager(filename=invalid_json_file)
        self.assertEqual(len(manager_invalid.notes), 0) # Should handle error and have empty notes
        os.remove(invalid_json_file)

if __name__ == '__main__':
    unittest.main()
