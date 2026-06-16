import pkg_resources, language_tool_python
from symspellpy import SymSpell

class TextCheckerModel:
    def __init__(self):
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.grammar_tool = language_tool_python.LanguageTool("en-US")
        
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
    
        self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

        bigram_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_bigramdictionary_en_243_342.txt"
        )
        
        self.sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)
        
    def correct_text(self, text):
        filtered_text = text.strip()
            
        suggestions = self.sym_spell.lookup_compound(
            phrase = filtered_text,
            max_edit_distance = 2,
            transfer_casing = True,
            ignore_term_with_digits = True,
            ignore_non_words = True,
            split_by_space = True
        )                    

        fixed_spell = suggestions[0].term if suggestions else text
            
        corrected_text = self.grammar_tool.correct(fixed_spell)
        matches = self.grammar_tool.check(text)
        
        error_words = []
        for rule in matches:
            start = rule.offset
            end = rule.offset + rule.error_length
            error_word = text[start:end]
            error_words.append(error_word)
        
        mistakes = ', '.join(error_words)
        
        return corrected_text, mistakes
    
    def __del__(self):
        try:
            self.grammar_tool.close()
        except: 
            pass