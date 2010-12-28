(function($, $S) {

  // Toggle all
  function onToggleAllClicked(e) {
    $('input:checkbox[name=attendees]').attr('checked', $(e.target).attr('checked') ? true : false);
  }

  // Enable / Disable actions
  function onCheckboxClicked(e) {
    var checked = $(".attendee.block input:checkbox").is(':checked');
    if(checked)
      $("#attendee-actions input:submit, #id_action").removeAttr("disabled")
    else
      $("#attendee-actions").find("select, input:submit").attr("disabled", "disabled");
  }

  $(function() {
    $('#attendees-check-all').click(onToggleAllClicked);
    $('input:checkbox').click(onCheckboxClicked);
  });

})(jQuery, Signupbox);