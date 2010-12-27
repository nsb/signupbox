(function($, $S) {

  function onToggleAllClicked(e) {
      $('input:checkbox[name=attendees]').attr('checked', $(e.target).attr('checked') ? true : false);
  }

  function onExportClicked(e) {
    $S.Modal.showAttachedModal($(e.target).parents('li'), $('#TemplateAttendeesExport').tmpl())
    e.preventDefault();
  }

  $(function() {
    $('#main').delegate(
      '#attendees-check-all', 'click', onToggleAllClicked
    ).delegate(
      '#attendees-export', 'click', onExportClicked
    );
  });

})(jQuery, Signupbox);