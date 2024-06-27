ace.define("ace/mode/concretize_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module){"use strict";
var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;
var DiffHighlightRules = function () {
    this.$rules = {
        "start": [
            {
                regex: "^(\#.*)$", // Comments
                token: ["comment"]
            },
            {
                regex: "^(Param )([^\:\ \(]*)(\:)", // Params
                token: [
                    "keyword", // "Param"
                    "variable", // Key, before colon
                    "text" // Colon
                ]
            },
            {
                regex: "^([^\:\ \(]*)(\ )", // Objects
                token: [
                    "constant", // "Class", before whitespace
                    "text" // Whitespace
                ]
            },
            {
                regex: "^([^\:\ \(]*)([\(])", // Constraints
                token: [
                    "support.function", // Constraint name, before parenthesis
                    "text" // Parenthesis
                ]
            }
        ]
    };
};
oop.inherits(DiffHighlightRules, TextHighlightRules);
exports.DiffHighlightRules = DiffHighlightRules;

});

ace.define("ace/mode/concretize",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/concretize_highlight_rules"], function(require, exports, module){"use strict";
var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var HighlightRules = require("./concretize_highlight_rules").DiffHighlightRules;
var Mode = function () {
    this.HighlightRules = HighlightRules;
};
oop.inherits(Mode, TextMode);
(function () {
    this.$id = "ace/mode/concretize";
    this.snippetFileId = "ace/snippets/concretize";
}).call(Mode.prototype);
exports.Mode = Mode;

});                
(function() {
    ace.require(["ace/mode/concretize"], function(m) {
        if (typeof module == "object" && typeof exports == "object" && module) {
            module.exports = m;
        }
    });
})();
