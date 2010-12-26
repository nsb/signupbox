(function($) {

  var onToggleAllClicked = function(e) {
      $('input:checkbox[name=attendees]').attr('checked', $(e.target).attr('checked') ? true : false);
  }

  $(function() {
    $('#main').delegate(
    '#check-all', 'click', onToggleAllClicked
    )
  });

})(jQuery);