$(function()
{
  var $wechat = $('footer #wechat-toggle');
  var $area = $('footer .am-footer-miscs');
  $wechat.click(function(evt)
  {
    evt.preventDefault();
    var loaded = ($wechat.data('load') == 'true');
    if (loaded)
    {
      $wechat.data('load', 'false');
      var $div = $area.find('#wechat-qr-img');
      $div.hide(400, function(evt)
      {
        $div.remove();
      });
    }
    else
    {
      $wechat.data('load', 'true');
      $area.append('<div id="wechat-qr-img"><img class="am-animation-scale-down am-img-responsive" src="https://dn-jolla.qbox.me/mywechat-service-banner.png"/></div>');
      $('html, body').animate({scrollTop: $(document).height()}, 1000);
    }
  });

  var $search = $('form.search');
  var $search_input = $search.find('[name="search"]');
  var $submit = $search.find('[type="submit"]');
  $search_input.focus(function(event){
    $search.css('opacity', '1');
  }).blur(function(event){
    $search.css('opacity', '0.3');
  });
  $search.submit(function(event)
  {
    $submit.button('loading');
    event.preventDefault();
    var search = $search_input.val();
    var plus_search = search.replace(/\s/g, '+');
    var url = $search.prop('action');
    if (url[url.length - 1] != '/')
        url += '/';
    url += (encodeURI(plus_search) + '/');
    window.open(url, $search.prop('target')).focus();
    $submit.button('reset');
  });

  $('.nav-icon1,.nav-icon2,.nav-icon3,.nav-icon4').click(function(){
    $(this).toggleClass('open');
  });
  $('#nav-menu').on('close.offcanvas.amui', function()
  {
    $('.nav-icon1,.nav-icon2,.nav-icon3,.nav-icon4').click();
  });

  $('[data-lang]').click(function(event)
  {
    event.preventDefault();
    var $this = $(this);
    var lang = $this.data('lang');
    console.log(lang, window.locale);
    if (lang == window.locale)
        return;
    change_lang(lang);
    window.location.href = location.pathname;
  });
});