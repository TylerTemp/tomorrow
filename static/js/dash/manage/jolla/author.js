var set_author = function(container, author)
{
  var $content = container.html(
    ('<div class="am-g">' +
      '<div class="am-u-sm-12 am-u-md-3">' +
        '<img class="am-round am-img-thumbnail" src="{11}">' +
      '</div>' +
      '<div class="am-u-sm-12 am-u-md-9">' +
        '<form class="am-form">' +
          '<fieldset>' +
            '<legend>{9}</legend>' +
            '<div class="am-form-group">' +
              '<label for="photo-{10}">{0}</label>' +
              '<input type="text" name="photo" value="{12}" id="photo-{10}" placeholder="{3}">' +
            '</div>' +
            '<div class="am-form-group">' +
              '<label for="description-{10}">{1}</label>' +
              '<textarea id="description-{10}" name="description" placeholder="{4}">{13}</textarea>' +
            '</div>' +
            '<div class="am-form-group">' +
              '<label for="translation-{10}">{2}</label>' +
              '<textarea id="translation-{10}" name="translation" placeholder="{5}">{14}</textarea>' +
            '</div>' +
            '<p>' +
              '<button type="submit" class="am-btn am-btn-success"><span class="am-icon-save"> {6}</span></button>' +
              '<button class="am-btn am-btn-default"><span class="am-icon-undo"> {7}</span></button>' +
              '<button class="am-btn am-btn-warning"><span class="am-icon-trash"> {8}</span></button>' +
            '</p>' +
          '</fieldset>' +
        '</form>' +
      '</div>' +
    '</div>').format(
      _('Photo'), _('Introduction'), _('Translation'),
      _('Enter photo url'), _('Enter introduction of author in English'), _('Enter the translation of the introduction'),
      _('Save'), _('Reset'), _('Delete'),
      author.name, author.id,
      author.photo || '/static/img/user.jpg',
      author.photo || '',
      author.description || '', author.translation || ''
    )
  );

  var $error_panel = $('<div></div>').appendTo(container);
  var set_error = function(msg, level)
  {
    if (!msg)
      return $error_panel.html('');
    var cls = level? 'am-alert-' + level: '';
    return $error_panel.html(
      '<div class="am-alert '+ cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' +
          msg +
        '</p>' +
      '</div>'
    );
  };

  var $buttons = $content.find('button');
  var $delete_btn = $buttons.eq(2);
  var $field = $content.find('fieldset');
  var $photo_input = $content.find('input');
  var $img_tag = $content.find('img');
  $photo_input.blur(function(event)
  {
    $img_tag.prop('src', $(this).val() || '/static/img/user.jpg');
  });
  $buttons.eq(1).click(function(event)
  {
    event.preventDefault();
    set_author(container, author);
  });
  $delete_btn.click(function(event)
  {
    event.preventDefault();
    $field.prop('disabled', true);
    var old_html = $delete_btn.html();
    $delete_btn.html('<i class="am-icon-spinner am-icon-pulse"></i>');
    $.ajax(
      settings = {
        data: {
          action: 'delete',
          name: author.name
        },
      type: 'post',
      beforeSend: function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_error(_("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown), 'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $delete_btn.html(old_html);
      $field.prop('disabled', false);
    }).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);
      if (obj.error != 0)
        return set_error(_("Sorry, a server error occured, please refresh and retry") + " ({0})".format(obj.error), 'danger');
      container.closest('div.am-panel').hide(400, function(evt)
      {
        $(this).remove();
      });
    });
  });
  $content.find('form').submit(function(event)
  {
    console.log('try submit');
    event.preventDefault();
    var $form = $(this);
    var dash_name = author.name.replace(/\s/g, '-');
    var $submit = $form.find('button[type="submit"]');
    var values = {};
    $.each($form.serializeArray(), function(_, field)
    {
        values[field.name] = field.value;
    });
    if ($.isEmptyObject(values))
    {
      console.log('Unexpected empty sumbit');
      return false;
    }

    values['name'] = author.name;
    $field.prop('disabled', true);
    var oldhtml = $submit.html();
    $submit.html('<i class="am-icon-refresh am-icon-spin"></i>');
    $.ajax(
      settings = {
        data: values,
        type: 'post',
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_error(_("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown), 'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.html(oldhtml);
      $field.prop('disabled', false);
    }).done(function(data, textStatus, jqXHR)
    {
      container.data('json', data);
      var obj = $.parseJSON(data);
      if (obj.error != 0)
        return set_error(_("Sorry, a server error occured, please refresh and retry") + " ({0})".format(obj.error), 'danger');
      set_author(container, obj);
    });

  });
};

$(function(event){
  $('#authors').find('[data-role="detail"]').each(function(idx, ele){
    $(this).on('open.collapse.amui', function(event){
      var $self = $(this);
      var $body = $self.find('.am-panel-bd');
      if ($body.data('json'))
      {
        console.log('from cache');
        set_author($body, $.parseJSON($body.data('json')));
      }
      else
      {
        $body.html('<i class="am-icon-spinner am-icon-pulse"></i>' + _('loading...'));
        $.ajax(
          settings={
            data: {
              name: $self.data('name')
            },
            type: 'get'
          }
        ).fail(function(jqXHR, textStatus, errorThrown){
          $body.html(
            '<div class="am-alert am-alert-danger" data-am-alert>' +
              '<p>' +
                _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown) +
              '</p>' +
            '</div>'
          );
        }).done(function(data, textStatus, jqXHR){
          $body.data('json', data);
          var author = $.parseJSON(data);
          set_author($body, author);
        });
      }
    });
  });
});
