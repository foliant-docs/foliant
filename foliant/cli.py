import cliar

class FoliantCLI(cliar.CLI):
    @cliar.add_aliases(["make"])
    def build(self, target, path = "."):
        print("Target: %s, path: %s" % (target, path))

    @cliar.add_aliases(["up"])
    def upload(self, doc, secret = ""):
        print("Docx: %s, secret: %s" % (doc, secret))

def main():
    FoliantCLI().parse()
