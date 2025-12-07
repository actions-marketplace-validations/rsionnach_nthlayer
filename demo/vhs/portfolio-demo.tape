# NthLayer Portfolio Demo
# Shows cross-vendor SLO aggregation across all services

Output portfolio-demo.gif

Require nthlayer

Set Shell "bash"
Set FontSize 16
Set Width 900
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set Framerate 30

# Run portfolio command
Type "nthlayer portfolio --dir examples/services"
Enter
Sleep 3s

# Let user see the output
Sleep 2s
