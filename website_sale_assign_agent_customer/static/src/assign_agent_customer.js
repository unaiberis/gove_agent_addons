odoo.define('my_module.my_script', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        // Create the input element
        var commentInput = $('<input>', {
            type: 'text',
            id: 'comment',
            name: 'comment'
        });

        // Create a <div> to hold the title and input box
        var container = $('<div>');

        // Add a title to the container
        container.append($('<label>', {
            for: 'comment',
            text: 'Comentario:'
        }));

        // Append the input element to the container
        container.append(commentInput);

        // Append the container to the form
        var form = $('form');
        form.append(container);

        // Add event listener to the dynamically created input
        commentInput.on('input', function () {
            // Log what is being written
            console.log('Texto en el cuadro de entrada:', commentInput.val());

            // Submit the form
            form.submit();
        });

        // Log message in the console
        console.log('Este mensaje aparecerá en todas las pantallas al refrescar.');
    });
});
