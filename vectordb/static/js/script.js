$(document).ready(function () {

    $("#upload-csv-button").click(function () {
        var fileInput = $("#csv-file")[0];
        if (fileInput.files.length === 0) return;
        var formData = new FormData();
        formData.append("csv_file", fileInput.files[0]);
        formData.append("csrfmiddlewaretoken", csrfToken);

        $.ajax({
            type: "POST",
            url: uploadCsvUrl,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                alert(response.message);
                $("#csv-file").val("");
            },
            error: function (error) {
                alert("CSV 업로드 오류");
            },
        });
    });

});
