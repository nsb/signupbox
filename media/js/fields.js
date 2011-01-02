(function($, $S) {

  function onAddOptionClicked(e) {
    var markup = $.tmpl($("#TemplateFieldsOptionAdd").html(), { "index" : this.index });
    $(e.target).parents('.option').after(markup);
    e.preventDefault();
  }

  function onRemoveOptionClicked(e) {
    $(e.target).parents('.option').remove();
    e.preventDefault();
  }

  function FieldView(options) {
    this.index = options.index;
    this.elm = options.element;

    var self = this;
    $(this.elm).delegate('.add', 'click', function() {onAddOptionClicked.apply(self, arguments)});
    $(this.elm).delegate('.remove', 'click', function() {onRemoveOptionClicked.apply(self, arguments)});
  }

  function setupFields() {
    $('.block.field').each(function(index, elm ) {
      new FieldView({index: index, element: elm});
    });
  }

  function onAddFieldClicked(e) {
    var markup = $("#TemplateFieldsAdd").html();
    var totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
    markup = $(markup.replace(/__prefix__/g, totalForms));
    new FieldView({index: totalForms, element: markup});
    $('#id_form-TOTAL_FORMS').val(++totalForms);
    $('#fields').append(markup);
    e.preventDefault();
  }

  $(function() {
    $('#add-field a').click(onAddFieldClicked);
    setupFields();
  });

})(jQuery, Signupbox);