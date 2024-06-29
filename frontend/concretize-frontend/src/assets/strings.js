export const DEFAULT_PARAMS = `# Search approach parameters
Param approach: "mhs";
Param algorithm_name: "nsga2";
Param timeout: 60;
Param num_of_scenarios: 3;
Param map: "Town02";

# Visual Settings
Param color_scheme: "default";
Param simulation_weather: "CloudyNoon";

# Scenario specfication
Car c1; isEgo; color: green;
Car c2; color: blue;

onRegion(c1, Road);
onRegion(c2, Junction);
distClose(c1, c2);
hasInFront(c1, c2);


`;
