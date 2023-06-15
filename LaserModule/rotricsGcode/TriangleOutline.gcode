G0 Z0
;TOOL_PATH_RENDER_METHOD_LINE
;----------- Start Gcode -----------
M2000;custom:line mode
M888 P1;custom:header is laser
M888 P14;custom:turn on cover fan
;-----------------------------------
M5
G0 F400
G1 F400
G0 X-1.11 Y324.47
M3 S127
G1 X-23.84 Y279.02
G1 X21.61 Y279.02
G1 X-1.11 Y324.47
M5
G0 X-1.91 Y300.95
;----------- End Gcode -------------
M888 P15;custom:turn off cover fan
;-----------------------------------
