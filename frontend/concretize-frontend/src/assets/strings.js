export const DEFAULT_PARAMS = `# MHS Mode
Param approach: "mhs";
Param algorithm_name: "nsga2";
Param timeout: 60;
Param map: "Town02";

# Complete Mode
#Param approach: "complete";
#Param map: "Town02";
#Param junction: 306;

# Settings
Param color_scheme: "default";
Param output_directory: "../output";
Param simulation_path: "../output/simResults.xml";
#Param simulation_ip: "localhost";
#Param simulation_port: 2000;
Param simulation_weather: "CloudyNoon";

# Scenario specfication
Car c1; isEgo; color: red;
Car c2; color: blue;

onRegion(c1, Road);
onRegion(c2, Junction);

distClose(c1, c2);



`;
