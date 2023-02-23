// custom javascript

$(document).ready(() => {
  console.log("check");
});

$(".btn").on("click", function () {
  $.ajax({
    url: "/tasks",
    data: { type: $(this).data("type") },
    method: "Post",
  })
    .done((res) => {
      getStatus(res.data.task_id);
    })
    .fail((err) => {
      console.log(err);
    });
});

function getStatus(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: "GET",
  })
    .done((res) => {
      const html = `
        <tr>
            <td>${res.data.task_id}</td>
            <td>${res.data.task_status}</td>
           
        <tr>`;
      $("#tasks").prepend(html);
      const taskStatus = res.data.task_status;
      //test code
      if (taskStatus === "finished") {
        console.log("trying download");
        $(".download").submit();
        $.ajax({
          url: "/download",
          method: "GET",
        })
          .done((res) => {
            console.log("success");
          })
          .fail((err) => {
            console.log("there was a problem");
          });
      }
      if (taskStatus === "finished" || taskStatus === "failed") return false;
      setTimeout(function () {
        getStatus(res.data.task_id);
      }, 1000);
    })
    .fail((err) => {
      console.log(err);
    });
}
