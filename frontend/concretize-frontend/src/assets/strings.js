export const DEFAULT_PARAMS = `Param approach: "mhs";
Param aggregation_strategy: "actors";
Param algorithm_name: "nsga2";
Param restart_time: -1;
Param history: "none";
Param num_of_mhs_runs: 10;
Param num_of_scenarios: 1;
Param color_scheme: "default";
Param hide_actors: false;
Param show_maneuvers: true;
Param show_exact_paths: true;
Param timeout: 60;
Param zoom_diagram: true;
Param map: "../maps/town02.xodr";
Param specification: "WEB EDITOR";
Param store_all_outcomes: false;
Param output_directory: "../output";
Param save_statistics_file: "../output/stats123.json";

Car c1; isEgo; color: red;
Car c2; color: blue;

onRegion(c1, Road);
onRegion(c2, Junction);

distClose(c1, c2);

`;
