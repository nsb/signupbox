Signupbox = {};
(function($, $S) {

  function onCloseClicked(e) {
    var selection = $('#attached-modal-overlay, #attached-modal-container');
    selection.fadeOut("fast", function() { selection.remove() });
    e.preventDefault();
  }

  function showAttachedModal(target, content) {
    var overlay = $('<div id="attached-modal-overlay"></div>').hide().appendTo(target);
    var container = $('<div id="attached-modal-container"></div>').hide().
      append('<div class="carat"></div><div class="content"></div>').
          css("top", $(target).outerHeight() - 5).
            find('.content').append(content).end().
              find('.close').click(onCloseClicked).end().
                appendTo(target);
    overlay.add(container).fadeIn("fast");
  }

  $S.Modal = {
    'showAttachedModal': showAttachedModal
  }
})(jQuery, Signupbox);