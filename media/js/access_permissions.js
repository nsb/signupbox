(function($, $S) {

  function onEditPermissionsClicked(e) {
    $(e.target).parents('.member').find('.remove').hide().end().find('.permissions').toggle(100);
    e.preventDefault();
  }

  function onRemoveFromAccountClicked(e) {
    $(e.target).parents('.member').find('.permissions').hide().end().find('.remove').toggle(100);
    e.preventDefault();
  }

  function onCancelInvitationClicked(e) {
    $(e.target).parents('.member').find('.cancel').toggle(100);
    e.preventDefault();
  }

  $(function() {
    $('#members .edit_permissions, #members .permissions_cancel').click(onEditPermissionsClicked)
    $('#members .remove_from_account, #members .remove_cancel').click(onRemoveFromAccountClicked)
    $('#members .cancel_invitation').click(onCancelInvitationClicked)
  });

})(jQuery, Signupbox);