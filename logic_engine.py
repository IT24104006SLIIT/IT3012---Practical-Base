# logic_engine.py
class KnowledgeBase:
    """A simple propositional Knowledge Base supporting Horn-clause forward chaining."""

    def __init__(self):
        self.facts = set()     
        self.rules = []       

    def tell_fact(self, fact_string):
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        self.facts.clear()

    def forward_chain(self):
        """Data-driven inference: repeatedly apply Modus Ponens until no new facts emerge."""
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    if all(p in self.facts for p in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True
