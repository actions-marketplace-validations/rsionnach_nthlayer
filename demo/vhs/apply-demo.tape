# NthLayer Apply Demo - Hero GIF
# Shows the core value prop: "20 hours of SRE work in 5 minutes"

Output apply-demo.gif

Require nthlayer

Set Shell "bash"
Set FontSize 16
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 20
Set Framerate 30

# Show the service spec
Type "cat service.yaml"
Enter
Sleep 1500ms

# Run nthlayer apply
Type "nthlayer apply service.yaml"
Enter
Sleep 3s

# Let user see the output
Sleep 2s
