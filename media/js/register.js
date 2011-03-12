(function($) {

  function onAddAttendeeClicked(e) {
    var markup = $("#AttendeeAddExtra").html();
    var totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
    markup = markup.replace(/__prefix__/g, totalForms);
    $('#id_form-TOTAL_FORMS').val(++totalForms);
    $('#attendee-forms').append(markup);
    e.preventDefault();
  }

  $(function() {
    $('#add-attendee a').click(onAddAttendeeClicked);

    $('a.new_window').click(function(){
      window.open(this.href, 'popup');
      return false;
    });

  });

})(jQuery);