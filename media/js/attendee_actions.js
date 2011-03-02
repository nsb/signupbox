(function($, $S) {

  // Toggle all
  function onToggleAllClicked(e) {
    $('input:checkbox[name=0-attendees]').attr('checked', $(e.target).attr('checked') ? true : false);
  }

  // Enable / Disable actions
  function onCheckboxClicked(e) {
    var checked = $(".attendee.block input:checkbox").is(':checked');
    if(checked)
      $("#attendee_actions .attendees input:submit, #attendee_actions .attendees select").removeAttr("disabled")
    else
      $("#attendee_actions .attendees").find("select, input:submit").attr("disabled", "disabled");
  }

  $(function() {
    $('#attendees-check-all').click(onToggleAllClicked);
    $('input:checkbox').click(onCheckboxClicked);
  });

})(jQuery, Signupbox);