var initCollapsible = function() {
    $(".collapsible .collapse-key").click(function(e) {
        toggle(this);
        e.stopPropagation();
        return false;
    });
}

var toggle = function(elem) {
    $(elem).next().slideToggle('fast');
    $(elem).toggleClass('expanded collapsed');
};
