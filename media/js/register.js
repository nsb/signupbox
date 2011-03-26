(function($) {

  var totalForms, maxForms;

  function onAddAttendeeClicked(e) {
    var markup = $("#AttendeeAddExtra").html();
    markup = markup.replace(/__prefix__/g, totalForms);
    $('#id_form-TOTAL_FORMS').val(++totalForms);
    $('#id_form-MAX_NUM_FORMS').val(--maxForms);
    $('#attendee-forms').append(markup);
    if (maxForms < 2)
      $('#add-attendee').hide();
    e.preventDefault();
  }

  $(function() {
    totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
    maxForms = parseInt($('#id_form-MAX_NUM_FORMS').val());
    if (maxForms < 2)
      $('#add-attendee').hide();

    $('#add-attendee a').click(onAddAttendeeClicked);

    $('a.new_window').click(function(e){
      window.open(this.href, 'popup');
      e.preventDefault();
    });

  });

})(jQuery);