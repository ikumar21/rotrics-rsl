G0 Z0
;TOOL_PATH_RENDER_METHOD_LINE
;----------- Start Gcode -----------
M2000;custom:line mode
M888 P1;custom:header is laser
M888 P14;custom:turn on cover fan
;-----------------------------------
M5
G0 F2000
G1 F2000
G0 X25.07 Y321.53
M3 S127
G1 X51.92 Y321.53
G1 X25.07 Y321.53
M5
;----------- End Gcode -------------
M888 P15;custom:turn off cover fan
;-----------------------------------
