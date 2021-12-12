Biomorph Evolve - Implementation of Dawkins' Blind Watchmaker Algorithm

Project site:
https://gatc.ca/projects/biomorph-evolve/


Dependencies:
Python 2.7+ (https://www.python.org/)
Pygame 1.9+ (https://www.pygame.org/)

Usage:
PyJ2D (https://gatc.ca/projects/pyj2d/) / Jython 2.2.1+ (https://www.jython.org/)
>Optional to port Pygame app to Java environment of JVM 6.0+ (https://www.java.com).
Pyjsdl (https://gatc.ca/projects/pyjsdl/) / Pyjs 0.8.1_dev (http://www.pyjs.org/)
>Optional to port Pygame app to JS environment of Web browser.
Pyjsdl-ts (https://gatc.ca/projects/pyjsdl-ts/) / Transcrypt (https://www.transcrypt.org/)
>Optional to port Pygame app to JS environment of Web browser.


Instructions:
Biomorph Evolve is an implementation of Richard Dawkins' Blind Watchmaker Algorithm, based on his article The Evolution of Evolvability in Artificial Life, SFI Studies in the Sciences of Complexity, 1988. The app is coded in Python and the Pygame library and run with the command 'python biomorph.py'. Alternatively, the app can run in the Java environment using Jython and the PyJ2D library with the command 'jython biomorph.py' or 'java -jar jython.jar biomorph.py'. The app can also run in the JavaScript environment using Pyjs compilation and the Pyjsdl library with the command '[pyjs_path]/bin/pyjsbuild -O biomorph.py --dynamic-link -o output', or using Transcrypt compilation and the Pyjsdl-ts library with the command 'transcrypt biomorpy.py' and launch with biomorph.html.

Controls
Select biomorph:
    LMouse
Repeat:
    Shift-LMouse
Reset:
    Shift-RMouse
    Key r
Exit:
    Key esc

Released under the GPL3 license (http://www.gnu.org/licenses/gpl.html).

