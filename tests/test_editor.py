import sys
sys.path.insert(0, '../backend')

from app.services.editor import DocumentEditor

def test_parse_add_operation():
    editor = DocumentEditor()
    
    instruction = "Add a requirement about user authentication"
    result = editor.parse_edit_request(instruction)
    
    assert result['operation'] == 'add'
    assert 'authentication' in result['content'].lower()
    print("✓ Add operation parsing works")

def test_parse_modify_operation():
    editor = DocumentEditor()
    
    instruction = "Change the executive summary to focus on security"
    result = editor.parse_edit_request(instruction)
    
    assert result['operation'] == 'modify'
    assert result['section'] == 'executive_summary'
    print("✓ Modify operation parsing works")

def test_section_detection():
    editor = DocumentEditor()
    
    instruction = "Update the functional requirements section"
    result = editor.parse_edit_request(instruction)
    
    assert result['section'] == 'functional_requirements'
    print("✓ Section detection works")

def test_apply_add_edit():
    editor = DocumentEditor()
    
    document = {
        "sections": {
            "functional_requirements": {
                "items": []
            }
        }
    }
    
    edit_request = {
        "operation": "add",
        "section": "functional_requirements",
        "content": "System must support OAuth 2.0"
    }
    
    updated = editor.apply_edit(document, edit_request)
    
    assert len(updated['sections']['functional_requirements']['items']) == 1
    print("✓ Apply add edit works")

if __name__ == "__main__":
    test_parse_add_operation()
    test_parse_modify_operation()
    test_section_detection()
    test_apply_add_edit()
    print("\n✅ All editor tests passed!")
