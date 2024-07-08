export const DEFAULT_PARAMS = `# Search approach parameters
Param approach: "mhs";
Param algorithm_name: "nsga2";
Param timeout: 60;
Param num_of_scenarios: 3;
Param map: "Town02";

# General Settings
Param color_scheme: "default";
Param simulation_weather: "CloudyNoon";
Param output_directory: "output";

# Scenario specification
Car c1; isEgo;
        color: green;
        speed: 5;
        controller: SimpleAgent;
Car c2; color: blue;
        speed: 10;
        controller: SimpleAgent;

onRegion(c1, Road);
onRegion(c2, Junction);
distClose(c1, c2);
hasInFront(c1, c2);


`;
