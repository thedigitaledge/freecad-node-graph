Feature: Node Graph UI Automation Behaviour
  As a FreeCAD user
  I want to visually create, edit, connect, and manage nodes in the Node Graph editor
  So that parametric models can be constructed through visual programming

  Scenario: Adding nodes from the Node Library task panel
    Given a fresh Node Graph document and editor workspace
    When I double click on the "BoxNode" item in the Node Library task panel
    Then the active editor graph should contain 1 node of type "BoxNode"
    And 1 node item should be displayed on the graphics scene

  Scenario: Connecting output and input sockets on the canvas
    Given a fresh Node Graph document and editor workspace
    And I add a "FloatNode" and a "BoxNode" to the graph
    When I connect the "Value" output of "FloatNode" to the "Length" input of "BoxNode"
    Then the graph should contain 1 connected edge between the nodes
    And 1 edge item should be visible on the graphics scene

  Scenario: Editing input node values through property controls
    Given a fresh Node Graph document and editor workspace
    And I add a "FloatNode" to the graph
    When I set the float node value to "42.5"
    Then the "FloatNode" value should equal 42.5
    And the output value of "FloatNode" should compute to 42.5

  Scenario: Deleting selected nodes from the canvas
    Given a fresh Node Graph document and editor workspace
    And I add a "FloatNode" and a "BoxNode" to the graph
    And I connect the "Value" output of "FloatNode" to the "Length" input of "BoxNode"
    When I select and delete the "BoxNode" on the canvas
    Then the graph should contain 1 node
    And the graph should contain 0 edges

  Scenario: Performing UI Undo and Redo operations
    Given a fresh Node Graph document and editor workspace
    When I add a "BoxNode" to the graph
    And I trigger UI undo
    Then the graph should contain 0 nodes
    When I trigger UI redo
    Then the active editor graph should contain 1 node of type "BoxNode"
