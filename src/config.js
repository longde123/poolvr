POOLVR.keyboardCommands = {

    turnLeft:     {buttons: [-Primrose.Input.Keyboard.LEFTARROW]},
    turnRight:    {buttons: [ Primrose.Input.Keyboard.RIGHTARROW]},
    driveForward: {buttons: [-Primrose.Input.Keyboard.W]},
    driveBack:    {buttons: [ Primrose.Input.Keyboard.S]},
    strafeLeft:   {buttons: [-Primrose.Input.Keyboard.A]},
    strafeRight:  {buttons: [ Primrose.Input.Keyboard.D]},
    floatUp:      {buttons: [ Primrose.Input.Keyboard.E]},
    floatDown:    {buttons: [-Primrose.Input.Keyboard.C]},

    moveToolUp:        {buttons: [Primrose.Input.Keyboard.O]},
    moveToolDown:      {buttons: [Primrose.Input.Keyboard.PERIOD]},
    moveToolForwards:  {buttons: [Primrose.Input.Keyboard.I]},
    moveToolBackwards: {buttons: [Primrose.Input.Keyboard.K]},
    moveToolLeft:      {buttons: [Primrose.Input.Keyboard.J]},
    moveToolRight:     {buttons: [Primrose.Input.Keyboard.L]},
    rotateToolCW:      {buttons: [Primrose.Input.Keyboard.U]},
    rotateToolCCW:     {buttons: [Primrose.Input.Keyboard.Y]},

    toggleVRControls: {buttons: [Primrose.Input.Keyboard.V],
                       commandDown: function(){app.toggleVRControls();}, dt: 0.25},
    toggleWireframe: {buttons: [Primrose.Input.Keyboard.NUMBER0],
                      commandDown: function(){app.toggleWireframe();}, dt: 0.25},
    resetVRSensor: {buttons: [Primrose.Input.Keyboard.Z],
                    commandDown: function(){app.resetVRSensor();}, dt: 0.25},

    resetTable: {buttons: [Primrose.Input.Keyboard.R],
                 commandDown: function(){POOLVR.resetTable();}, dt: 0.5},

    autoPosition: {buttons: [Primrose.Input.Keyboard.P],
                   commandDown: function(){POOLVR.autoPosition(POOLVR.avatar);}, dt: 0.5},

    toggleMenu: {buttons: [Primrose.Input.Keyboard.SPACEBAR],
                 commandDown: function(){POOLVR.toggleMenu();}, dt: 0.25},

    nextBall: {buttons: [Primrose.Input.Keyboard.ADD],
               commandDown: function(){POOLVR.selectNextBall();}, dt: 0.5},

    prevBall: {buttons: [Primrose.Input.Keyboard.SUBTRACT],
               commandDown: function(){POOLVR.selectNextBall(-1);}, dt: 0.5}
};
POOLVR.keyboardCommands = makeObjectArray(POOLVR.keyboardCommands, 'name');
POOLVR.keyboard = new Primrose.Input.Keyboard("keyboard", window, POOLVR.keyboardCommands);

var DEADZONE = 0.2;
POOLVR.gamepadCommands = {

    strafe:   {axes: [ Primrose.Input.Gamepad.LSX], deadzone: DEADZONE},
    drive:    {axes: [ Primrose.Input.Gamepad.LSY], deadzone: DEADZONE},
    float:    {axes: [-Primrose.Input.Gamepad.LSY], deadzone: DEADZONE},
    dheading: {axes: [-Primrose.Input.Gamepad.LSX], deadzone: DEADZONE},
    pitch:    {axes: [ Primrose.Input.Gamepad.LSY], deadzone: DEADZONE,
               integrate: true, max: 0.5 * Math.PI, min: -0.5 * Math.PI},
    toggleFloatMode: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.leftStick],
                      commandDown: function(){POOLVR.avatar.floatMode=true;},
                      commandUp: function(){POOLVR.avatar.floatMode=false;}},

    toolStrafe: {axes: [ Primrose.Input.Gamepad.RSX], deadzone: DEADZONE},
    toolDrive:  {axes: [ Primrose.Input.Gamepad.RSY], deadzone: DEADZONE},
    toolFloat:  {axes: [-Primrose.Input.Gamepad.RSY], deadzone: DEADZONE},
    toggleToolFloatMode: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.rightStick],
                          commandDown: function(){POOLVR.avatar.toolMode=true;},
                          commandUp: function(){POOLVR.avatar.toolMode=false;}},

    resetVRSensor: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.back],
                    commandDown: function(){app.resetVRSensor();}, dt: 0.25},

    nextBall: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.rightBumper],
               commandDown: function(){POOLVR.selectNextBall();}, dt: 0.25},

    prevBall: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.leftBumper],
               commandDown: function(){POOLVR.selectNextBall(-1);}, dt: 0.25},

    autoPosition: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.Y],
                   commandDown: function(){POOLVR.autoPosition(POOLVR.avatar);}, dt: 0.25},

    toggleMenu: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.start],
                 commandDown: function(){POOLVR.toggleMenu();}, dt: 0.25},

    saveConfig: {buttons: [Primrose.Input.Gamepad.XBOX_BUTTONS.right],
                 commandDown: function(){POOLVR.saveConfig();}, dt: 0.25}

};


POOLVR.gamepadCommands = makeObjectArray(POOLVR.gamepadCommands, 'name');
POOLVR.gamepad = new Primrose.Input.Gamepad("gamepad", POOLVR.gamepadCommands);
POOLVR.gamepad.addEventListener("gamepadconnected", function(id) {
    if (!this.isGamepadSet()) {
        this.setGamepad(id);
        console.log("gamepad " + id + " connected");
    }
}.bind(POOLVR.gamepad), false);


if (POOLVR.config.useShadowMap) {
    POOLVR.config.useBasicMaterials = false;
}

POOLVR.config.toolOptions = POOLVR.config.toolOptions || {};
POOLVR.config.toolOptions.toolLength   = URL_PARAMS.toolLength   || POOLVR.config.toolOptions.toolLength;
POOLVR.config.toolOptions.toolRadius   = URL_PARAMS.toolRadius   || POOLVR.config.toolOptions.toolRadius;
POOLVR.config.toolOptions.toolMass     = URL_PARAMS.toolMass     || POOLVR.config.toolOptions.toolMass;
POOLVR.config.toolOptions.toolOffset   = URL_PARAMS.toolOffset   || POOLVR.config.toolOptions.toolOffset;
POOLVR.config.toolOptions.toolRotation = URL_PARAMS.toolRotation || POOLVR.config.toolOptions.toolRotation;
POOLVR.config.toolOptions.tipShape     = URL_PARAMS.tipShape     || POOLVR.config.toolOptions.tipShape;

POOLVR.config.toolOptions.host = URL_PARAMS.host;
POOLVR.config.toolOptions.port = URL_PARAMS.port;

POOLVR.toolOptions = combineObjects(POOLVR.config.toolOptions, {
    useBasicMaterials: POOLVR.config.useBasicMaterials
});

POOLVR.config.synthSpeakerVolume = URL_PARAMS.synthSpeakerVolume || POOLVR.config.synthSpeakerVolume || 0.25;

POOLVR.config.initialPosition = POOLVR.config.initialPosition || [0, 1, 1.86];

POOLVR.configName = URL_PARAMS.configName || 'default';

POOLVR.saveConfig = function () {
    "use strict";
    POOLVR.config.toolOptions.toolOffset = [POOLVR.toolRoot.position.x, POOLVR.toolRoot.position.y, POOLVR.toolRoot.position.z];
    POOLVR.config.toolOptions.toolRotation = POOLVR.toolRoot.rotation.y;
    localStorage.setItem(POOLVR.configName, JSON.stringify(POOLVR.config));
    console.log('saved configuration:');
    console.log(JSON.stringify(POOLVR.config, undefined, 2));
};


POOLVR.loadConfig = function () {
    "use strict";
    var localStorageConfig = localStorage.getItem(POOLVR.configName);
    if (localStorageConfig) {
        localStorageConfig = JSON.parse(localStorageConfig);
        for (var k in localStorageConfig) {
            if (POOLVR.config.hasOwnProperty(k)) {
                POOLVR.config[k] = localStorageConfig[k];
            }
        }
        console.log('loaded configuration:');
        console.log(JSON.stringify(POOLVR.config, undefined, 2));
    }
};
