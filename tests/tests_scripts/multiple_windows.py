from ghost import Ghost

gh = Ghost(wait_timeout=10000, display=True)
for i in range(10):
    
    page, name = gh.create_page(wait_timeout=10000)
    page.open("http://www.google.com")
    import pdb; pdb.set_trace()
    print i
    page.wait_for_text("no existe este texto")
import pdb; pdb.set_trace()