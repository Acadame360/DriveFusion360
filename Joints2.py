#Author-
#Description-

from pickle import TRUE
import adsk.core, adsk.fusion, adsk.cam, traceback

# Global variable used to maintain a reference to all event handlers.
handlers = []

# Other global variables
commandName = "MoveRobot"
app = adsk.core.Application.get()
if app:
    ui = app.userInterface
    
revoluteJoint1 = None
revoluteJoint2 = None
revoluteJoint3 = None
revoluteJoint4 = None
isReverseUpDown = False
isReverseLeftRight = False
revolutionStep = 0.1

hasIPJ = 0


# Event handler for the keyDown event.
class MyKeyDownHandler(adsk.core.KeyboardEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.KeyboardEventArgs.cast(args)
            keyCode = eventArgs.keyCode    
                
            if keyCode == adsk.core.KeyCodes.InsertKeyCode:
                if isReverseUpDown:
                    diffVal = -revolutionStep
                else:
                    diffVal = revolutionStep
                motion = revoluteJoint1.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.EndKeyCode:
                if isReverseUpDown:
                    diffVal = revolutionStep
                else:
                    diffVal = -revolutionStep               
                motion = revoluteJoint1.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.DownKeyCode:
                if isReverseLeftRight:
                    diffVal = -revolutionStep
                else:
                    diffVal = revolutionStep                
                motion = revoluteJoint2.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.PageDownKeyCode:
                if isReverseLeftRight:
                    diffVal = revolutionStep
                else:
                    diffVal = -revolutionStep                
                motion = revoluteJoint2.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.LeftKeyCode:
                if isReverseLeftRight:
                    diffVal = -revolutionStep
                else:
                    diffVal = revolutionStep                
                motion = revoluteJoint3.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.RightKeyCode:
                if isReverseLeftRight:
                    diffVal = revolutionStep
                else:
                    diffVal = -revolutionStep                
                motion = revoluteJoint3.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal 
            elif keyCode == adsk.core.KeyCodes.HomeKeyCode:
                if isReverseLeftRight:
                    diffVal = -revolutionStep
                else:
                    diffVal = revolutionStep                
                motion = revoluteJoint4.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.UpKeyCode:
                if isReverseLeftRight:
                    diffVal = revolutionStep
                else:
                    diffVal = -revolutionStep                
                motion = revoluteJoint4.jointMotion
                motion.rotationValue = motion.rotationValue + diffVal
            elif keyCode == adsk.core.KeyCodes.PageUpKeyCode:
                global hasIPJ
                if (hasIPJ == 0):
                    # Create the AsBuiltJointInput
                    # Get the root component of the active design
                    
                    product = app.activeProduct
                    design = adsk.fusion.Design.cast(product)
                    if design.snapshots.hasPendingSnapshot: design.snapshots.add() # capture position
                    rootComp = design.rootComponent

                    occ1 =rootComp.occurrences.itemByName('box:1')
                    occ2 =rootComp.occurrences.itemByName('grab:1')
                    #txt=occ1.name
                    asBuiltJoints_ = rootComp.asBuiltJoints
                    asBuiltJointInput = asBuiltJoints_.createInput(occ1, occ2, None)

                    # Create the AsBuiltJoint
                    asBuiltJoints_.add(asBuiltJointInput)
                    
                    hasIPJ= 1
            elif keyCode == adsk.core.KeyCodes.EqualKeyCode:
                
                # delete the AsBuiltJointInput
                if (hasIPJ == 1):

                    product = app.activeProduct
                    design = adsk.fusion.Design.cast(product)

                    rootComp = design.rootComponent
                    numjoints = rootComp.asBuiltJoints.count
                    if numjoints == 1:

                        asBuiltJoints_ = rootComp.asBuiltJoints
                        res11 = asBuiltJoints_.item(0).deleteMe()

                        if design.snapshots.hasPendingSnapshot: design.snapshots.add() # capture position
                                        
                        
                        hasIPJ=0                

            # Refresh the view to show the change
            vp = app.activeViewport
            vp.refresh()
            
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))              

# Event handler for the inputChanged event.
class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)

        commandInput = eventArgs.input
        if commandInput.id == commandName + '_step':
            global revolutionStep
            revolutionStep = commandInput.value
        elif commandInput.id == commandName + '_reverseUpDown':
            global isReverseUpDown
            isReverseUpDown = commandInput.value
        elif commandInput.id == commandName + '_reverseLeftRight':
            global isReverseLeftRight
            isReverseLeftRight = commandInput.value
        
        
# Event handler for the executePreview event.
class MyExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        
        # Make it accept the changes whatever happens
        eventArgs.isValidResult = True
        

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            command = adsk.core.Command.cast(args.command)
            
            # Subscribe to the various command events
            onInputChanged = MyInputChangedHandler()
            command.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            onExecutePreview = MyExecutePreviewHandler()
            command.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)
        
            onKeyDown = MyKeyDownHandler()
            command.keyDown.add(onKeyDown)
            handlers.append(onKeyDown)
            
            onDestroy = MyCommandDestroyHandler()
            command.destroy.add(onDestroy)
            handlers.append(onDestroy)
            
            inputs = command.commandInputs
            inputs.addTextBoxCommandInput(
                commandName + '_usage', 
                'Usage:', 
                'Use Xbox controller to drive the robot arm', 2, 
                True);
            inputs.addTextBoxCommandInput(
                commandName + '_usage', 
                'Usage:', 
                'Use button A to pickup green box', 2, 
                True);
            inputs.addTextBoxCommandInput(
                commandName + '_usage', 
                'Usage:', 
                'Use button B to drop box', 2, 
                True);
            inputs.addValueInput(
                commandName + '_step', 
                'Rotation step: ',
                'deg',
                adsk.core.ValueInput.createByReal(revolutionStep))                
            #inputs.addBoolValueInput(
            #    commandName + '_reverseUpDown',
            #    'Reverse Up/Down direction',
            #    True,
            #    '',
            #    isReverseUpDown)
            #inputs.addBoolValueInput(
            #    commandName + '_reverseLeftRight',
            #    'Reverse Left/Right direction',
            #    True,
            #    '',
            #    isReverseLeftRight) 
                
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))              
            
            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            commandDefinitions = ui.commandDefinitions
            # Check the command exists or not
            cmdDef = commandDefinitions.itemById(commandName)
            if cmdDef:
                cmdDef.deleteMe                
                
            # When the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
            
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))        
            
            
def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
            
        # Get selected Revolute Joints to work on 
        #selections = app.userInterface.activeSelections
        #if selections.count != 2:
        #    ui.messageBox("The 2 revolute joints you want to control need to be selected before running the command!")
        #    return
        
        # Get the root component of the active design
        rootComp = design.rootComponent

        joints=rootComp.joints
        global revoluteJoint1, revoluteJoint2, revoluteJoint3, revoluteJoint4
        revoluteJoint1 = joints.itemByName('Rev1')
        revoluteJoint2 = joints.itemByName('Rev2')   
        revoluteJoint3 = joints.itemByName('Rev3')
        revoluteJoint4 = joints.itemByName('Rev4')      

        
            
        commandDefinitions = ui.commandDefinitions
        # Check the command exists or not
        cmdDef = commandDefinitions.itemById(commandName)
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition(
                commandName, commandName, commandName, '') 

        # Subscribe to events 
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        
        # Run the command
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # Prevent this module from being terminated when the script returns, 
        # because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))