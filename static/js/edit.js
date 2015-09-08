$(function(evt)
{
  var preview = function(content)
  {
    if ($preview.data('lock') == 'true')
      return;
    $preview.html(content);
  }


  var count_timer = function()
  {
    var interval = parseFloat($interval.val());
    if (isNaN(interval) || (interval < 0))
      return;
    timer = setTimeout(function(){preview($mdEditor.getHtml()); count_timer()}, interval * 1000);
  }


  var stop_timer = function()
  {
    clearTimeout(timer);
  }


  var $preview = $('#preview');
  var $interval = $('#seconds');
  var $online_preview = $('#online-preview');
  // var toHtml = markdown.toHtml;
  var converter = new showdown.Converter();
  var $mdEditor = $('#mdEditor').markdownEditor({
    toHtml: converter.makeHtml,
    uploadImageUrl: IMGUPLOADURL,
    uploadFileUrl: FILEUPLOADURL
  });

  timer = setTimeout(function(){preview($mdEditor.getHtml()); count_timer()}, 0);

  $('#tag').tagsinput();

  $('#hide-preview').click(function(evt)
  {
    var hidden = $(this).hasClass('am-active');
    if (!hidden)
    {
      $mdEditor.parent().removeClass('am-u-md-6');
      $preview.parent().removeClass('am-u-md-6').hide();
    }
    else
    {
      $mdEditor.parent().addClass('am-u-md-6');
      $preview.parent().addClass('am-u-md-6').show();
    }
  });

  $('#slug-test').click(function(evt)
  {
    evt.preventDefault();
    var slug = $.trim($('#slug').val());
    if (!slug)
      return;
    var $slug_test = $(this);
    $slug_test
        .removeClass('am-btn-success am-btn-warning am-btn-danger am-loading')
        .prop('disabled', true)
        .addClass('am-btn-default')
        .html('<i class="am-icon-spinner am-icon-pulse"></i>');

    $.ajax(settings={
      data: {
        slug: slug,
        test: true,
      },
      method: 'get',
    }).done(function(data, textStatus, jqXHR)
    {
      var result = parseInt(data);
      switch (result)
      {
        case -1:
          $slug_test.html('<span class="am-icon-beer"> ' + _('Same') + '</span>');
          break;
        case 0:
          $slug_test
            .removeClass('am-btn-default')
            .addClass('am-btn-warning')
            .html('<span class="am-icon-times"> ' + _('Taken') + '</span>');
          break;
        case 1:
          $slug_test
            .removeClass('am-btn-default')
            .addClass('am-btn-success')
            .html('<span class="am-icon-check"></span>');
          break;
      }
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      $slug_test
        .addClass('am-btn-danger')
        .html('<span class="am-icon-bug"> '+ jqXHR.status + '</span>')
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown){
      $slug_test
        .prop('disabled', false)
        .removeClass('am-loading');
    });
  })

  $('#slug').on('input', function(evt)
  {
    var $slug_test = $('#slug-test');
    if (!$slug_test.hasClass('am-loading'))
      $slug_test
        .removeClass('am-btn-success am-btn-danger am-btn-warning')
        .addClass('am-btn-default')
        .html('<span class="am-icon-question"> {0}</span>'.format(_('Test')))
        .prop('disabled', !$.trim($(this).val()))
  });

  $mdEditor.on('input', function(evt)
  {
    $preview.data('lock', 'false');
    if (!$online_preview.prop('disabled'))
      $online_preview
        .removeClass('am-btn-success am-btn-default am-btn-danger')
        .addClass('am-btn-warning')
        .html('<span class="am-icon-eye"></span>')
  });

  $('#local-preview').click(function(evt)
  {
    evt.preventDefault();
    $preview.data('lock', 'false');
    if (!$online_preview.prop('disabled'))
      $online_preview
        .removeClass('am-btn-success am-btn-default')
        .addClass('am-btn-warning')
        .html('<span class="am-icon-eye"></span>');
    preview($mdEditor.getHtml());
  });

  $interval.change(function(evt)
  {
    stop_timer();
    var interval = parseFloat($interval.val());
    if (isNaN(interval) || (interval < 0))
      return;
    count_timer();
  });

  $online_preview.click(function(evt)
  {
    var md = $mdEditor.val();
    var html = $mdEditor.getHtml();
    $preview.data('lock', 'false');
    preview(html);
    $online_preview
      .removeClass('am-btn-danger am-btn-warning am-btn-success')
      .addClass('am-btn-default')
      .html('<i class="am-icon-spinner am-icon-pulse"></i>')
      .prop('disabled', true);

    $.ajax(
      '/api/md/html/',
      settings={
        data: {'content': md},
        method: (md.length < 700? 'get': 'post')
      }
    ).done(function(data, textStatus, jqXHR)
    {
      $preview.data('lock', 'false');
      preview(data);
      $preview.data('lock', 'true');
      $online_preview
        .removeClass('am-btn-danger')
        .addClass('am-btn-success')
        .html('<span class="am-icon-check"></span>');
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      $online_preview
        .removeClass('am-btn-success')
        .addClass('am-btn-danger')
        .html('<span class="am-icon-times"></span>');
      console.log(jqXHR.status + errorThrown);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $online_preview
        .removeClass('am-btn-default am-btn-warning')
        .prop('disabled', false);
    });
  });

  $('form').submit(function(evt)
  {
    evt.preventDefault();
    $form = $(this);
    $fieldset = $form.find('fieldset');
    $submit = $form.find('[type="submit"]');

    var values = {};
    $.each($form.serializeArray(), function(i, field)
    {
      values[field.name] = field.value;
    });

    $fieldset.prop('disabled', true);
    $submit.button('loading');

    $.ajax(settings={
      data: values,
      method: 'post',
      beforeSend: function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    }).done(function(data, textStatus, jqXHR)
    {
      window.location.href = $.parseJSON(data).redirect;
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      alert(jqXHR.status + errorThrown)
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $fieldset.prop('disabled', false);
      $submit.button('reset');
    });

  });

});
