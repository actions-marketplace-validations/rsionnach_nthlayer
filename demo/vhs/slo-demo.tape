# NthLayer SLO Demo
# Shows SLO inspection commands

Output slo-demo.gif

Require nthlayer

Set Shell "bash"
Set FontSize 16
Set Width 900
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set Framerate 30

# Show SLO list
Type "nthlayer slo list --dir examples/services"
Enter
Sleep 2500ms

# Show SLO details for a specific service
Type "nthlayer slo show examples/services/payment-api.yaml"
Enter
Sleep 2500ms

# Let user see the output
Sleep 2s
