ace.define("ace/mode/concretize_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module){"use strict";
var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;
var DiffHighlightRules = function () {
    this.$rules = {
        "start": [
            {
                regex: "^([^\:\ \(]*)(\:)", // Params
                token: [
                    "variable", // Key, before colon
                    "text" // Colon
                ]
            },
            {
                regex: "^([^\:\ \(]*)(\ )", // Objects
                token: [
                    "keyword", // "Class", before whitespace
                    "text" // Whitespace
                ]
            },
            {
                regex: "^([^\:\ \(]*)([\(])", // Constraints
                token: [
                    "support.function", // Constraint name, before parenthesis
                    "text" // Parenthesis
                ]
            },
            // {
            //     regex: "^(?:\\*{15}|={67}|-{3}|\\+{3})$",
            //     token: "punctuation.definition.separator.diff",
            //     "name": "keyword"
            // }, {
            //     regex: "^(@@)(\\s*.+?\\s*)(@@)(.*)$",
            //     token: [
            //         "constant",
            //         "constant.numeric",
            //         "constant",
            //         "comment.doc.tag"
            //     ]
            // }, {
            //     regex: "^(\\d+)([,\\d]+)(a|d|c)(\\d+)([,\\d]+)(.*)$",
            //     token: [
            //         "constant.numeric",
            //         "punctuation.definition.range.diff",
            //         "constant.function",
            //         "constant.numeric",
            //         "punctuation.definition.range.diff",
            //         "invalid"
            //     ],
            //     "name": "meta."
            // }, {
            //     regex: "^(\\-{3}|\\+{3}|\\*{3})( .+)$",
            //     token: [
            //         "constant.numeric",
            //         "meta.tag"
            //     ]
            // }, {
            //     regex: "^([!+>])(.*?)(\\s*)$",
            //     token: [
            //         "support.constant",
            //         "text",
            //         "invalid"
            //     ]
            // }, {
            //     regex: "^([<\\-])(.*?)(\\s*)$",
            //     token: [
            //         "support.function",
            //         "string",
            //         "invalid"
            //     ]
            // }, {
            //     regex: "^(diff)(\\s+--\\w+)?(.+?)( .+)?$",
            //     token: ["variable", "variable", "keyword", "variable"]
            // }, {
            //     regex: "^Index.+$",
            //     token: "variable"
            // }, {
            //     regex: "^\\s+$",
            //     token: "text"
            // }, {
            //     regex: "\\s*$",
            //     token: "invalid"
            // }
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
