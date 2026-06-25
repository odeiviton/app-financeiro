(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // === FILTER CATEGORY BY TYPE ===
    var tipoSelect = document.getElementById('filtro_tipo');
    var catSelect = document.getElementById('filtro_categoria');
    if (tipoSelect && catSelect) {
      tipoSelect.addEventListener('change', function () {
        var tipo = this.value;
        var selectedVal = catSelect.value;
        catSelect.innerHTML = '<option value="">Todas</option>';
        if (tipo) {
          categoriasData
            .filter(function (c) { return c.tipo === tipo; })
            .forEach(function (c) {
              var opt = document.createElement('option');
              opt.value = c.id;
              opt.textContent = c.nome;
              if (String(c.id) === selectedVal) opt.selected = true;
              catSelect.appendChild(opt);
            });
        } else {
          categoriasData.forEach(function (c) {
            var opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nome;
            if (String(c.id) === selectedVal) opt.selected = true;
            catSelect.appendChild(opt);
          });
        }
      });
    }

    // === CATEGORY FILTER IN FORM (tipo change) ===
    var formTipo = document.getElementById('form_tipo');
    var formCategoria = document.getElementById('form_categoria');
    if (formTipo && formCategoria) {
      formTipo.addEventListener('change', function () {
        var tipo = this.value;
        var selectedVal = formCategoria.value;
        formCategoria.innerHTML = '<option value="">Selecione...</option>';
        categoriasData
          .filter(function (c) { return c.tipo === tipo; })
          .forEach(function (c) {
            var opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nome;
            if (String(c.id) === selectedVal) opt.selected = true;
            formCategoria.appendChild(opt);
          });
        formCategoria.disabled = !tipo;
      });
      if (formTipo.value) formTipo.dispatchEvent(new Event('change'));
    }

    // === MODAL ===
    var modalOverlay = document.getElementById('modalTransacao');
    if (modalOverlay) {
      document.querySelectorAll('[data-open-modal]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          modalOverlay.classList.add('show');
          document.body.style.overflow = 'hidden';
        });
      });
      modalOverlay.querySelector('.modal-close').addEventListener('click', closeModal);
      modalOverlay.addEventListener('click', function (e) {
        if (e.target === modalOverlay) closeModal();
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeModal();
      });
    }
    function closeModal() {
      if (modalOverlay) modalOverlay.classList.remove('show');
      document.body.style.overflow = '';
    }

    // === CONFIRM EXCLUSION ===
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
      if (el.tagName === 'FORM') {
        el.addEventListener('submit', function (e) {
          if (!confirmarExclusao(this.dataset.confirm)) {
            e.preventDefault();
          }
        });
      } else {
        el.addEventListener('click', function (e) {
          if (!confirmarExclusao(this.dataset.confirm)) {
            e.preventDefault();
          }
        });
      }
    });

    // === DROPDOWN (top nav) ===
    document.querySelectorAll('.dropdown > a').forEach(function (toggle) {
      toggle.addEventListener('click', function (e) {
        e.preventDefault();
        var menu = this.nextElementSibling;
        if (menu && menu.classList.contains('dropdown-menu')) {
          menu.classList.toggle('show');
        }
      });
    });
    document.addEventListener('click', function (e) {
      document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
        if (!menu.parentElement.contains(e.target)) {
          menu.classList.remove('show');
        }
      });
    });

    // === FLASH AUTO-DISMISS ===
    document.querySelectorAll('.flash').forEach(function (flash) {
      setTimeout(function () {
        flash.classList.add('hiding');
        setTimeout(function () { flash.remove(); }, 300);
      }, 4000);
    });

    // === LOADING STATE ON FORMS ===
    document.querySelectorAll('form[data-loading]').forEach(function (form) {
      form.addEventListener('submit', function () {
        var btn = this.querySelector('[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.innerHTML = '<span class="spinner"></span>';
        }
      });
    });

  });

  function confirmarExclusao(msg) {
    return confirm(msg || 'Tem certeza que deseja excluir?');
  }

})();
