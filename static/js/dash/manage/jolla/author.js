var set_author = function(container, author)
{
  container.html(

  );
}

$(document).ready(function(evt){
  $('#authors').find('[data-role="detail"]').each(function(idx, ele){
    $(this).on('open.collapse.amui', function(evt){
      var self = $(this);
      var body = self.find('.am-panel-bd');
      if (self.data('json'))
      {

      }
      else
      {
        // body.html('<i class="am-icon-spinner am-icon-pulse"></i>' + _('loading...'));
        $.ajax(
          settings={
            'data': {
              'name': self.data('name')
            },
            'type': 'get'
          }
        ).fail(function(jqXHR, textStatus, errorThrown){
          body.html(
            '<div class="am-alert am-alert-danger" data-am-alert>' +
              '<p>' +
                _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown) +
              '</p>' +
            '</div>'
          );
        }).done(function(data, textStatus, jqXHR){
          var author = $.parseJSON(data);

        });
      }
    });
  });
});
