Signupbox = {};
(function($, $S) {

  function onCloseClicked(e) {
    $('#attached-modal-overlay, #attached-modal-container').remove();
    e.preventDefault();
  }

  function showAttachedModal(target, content) {
    $('<div id="attached-modal-overlay"></div>').appendTo(target);
    $('<div id="attached-modal-container"></div>').
      append(content).
        css("top", $(target).outerHeight()).
          appendTo(target).
            find('.close').click(onCloseClicked);
  }

  $S.Modal = {
    'showAttachedModal': showAttachedModal
  }
})(jQuery, Signupbox);