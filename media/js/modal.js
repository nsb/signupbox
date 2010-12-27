Signupbox = {};
(function($, $S) {

  function showAttachedModal(target, content) {
    $('<div id="attached-modal-overlay"></div>').appendTo(target);
    $('<div id="attached-modal-container"></div>').append(content).appendTo(target);
  }

  $S.Modal = {
    'showAttachedModal': showAttachedModal
  }
})(jQuery, Signupbox);