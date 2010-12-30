(function($, $S) {

  function onAddFieldClicked(e) {
    var markup = $("#TemplateFieldsAdd").html();
    var totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
    markup = markup.replace(/__prefix__/g, totalForms);
    $('#id_form-TOTAL_FORMS').val(++totalForms);
    $('#fields').append(markup);
    e.preventDefault();
  }

  $(function() {
    $('#add-field a').click(onAddFieldClicked);
  });

})(jQuery, Signupbox);