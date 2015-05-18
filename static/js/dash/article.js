$(document).ready(function()
{

  $("button[data-role='delete']").click(function(evt)
  {
    console.log('click');
    evt.preventDefault();
  });

});
