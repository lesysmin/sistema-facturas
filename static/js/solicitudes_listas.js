// static/js/solicitudes_listas.js
// Funciones compartidas para lista.html y lista_jefe.html

class SolicitudesLista {
    constructor(config = {}) {
        this.config = {
            filters: ['estado', 'prioridad'],
            ...config
        };
        this.elements = {};
        this.state = {
            currentSort: { field: 'fecha', direction: 'desc' },
            pdfDoc: null,
            pageNum: 1,
            pageRendering: false,
            pageNumPending: null,
            scale: 1.5
        };
        
        this.init();
    }

    init() {
        this.setupElements();
        this.setupEventListeners();
        this.initPDFJS();
        this.updateTable();
    }

    setupElements() {
        // Elementos comunes
        this.elements = {
            search: document.getElementById('searchInput'),
            clearFilters: document.getElementById('clearFilters'),
            resetSearch: document.getElementById('resetSearch'),
            noResults: document.getElementById('noResults'),
            resultCount: document.getElementById('resultCount'),
            solicitudItems: document.querySelectorAll('.solicitud-item'),
            sortableHeaders: document.querySelectorAll('.sortable'),
            
            // Modal PDF
            pdfModal: document.getElementById('pdfModal') ? new bootstrap.Modal(document.getElementById('pdfModal')) : null,
            modalSolicitudNumero: document.getElementById('modalSolicitudNumero'),
            downloadFromModal: document.getElementById('downloadFromModal'),
            canvas: document.getElementById('pdfCanvas'),
            pageNum: document.getElementById('pageNum'),
            pageCount: document.getElementById('pageCount'),
            prevPage: document.getElementById('prevPage'),
            nextPage: document.getElementById('nextPage')
        };

        // Contexto del canvas si existe
        if (this.elements.canvas) {
            this.elements.ctx = this.elements.canvas.getContext('2d');
        }

        // Elementos específicos por template
        if (this.config.filters) {
            this.config.filters.forEach(filter => {
                const filterName = `filter${filter.charAt(0).toUpperCase() + filter.slice(1)}`;
                this.elements[filter] = document.getElementById(filterName);
            });
        }
    }

    initPDFJS() {
        // Configurar PDF.js solo si está disponible
        if (typeof pdfjsLib !== 'undefined') {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
        }
    }

    // PDF Functions
    async loadPdf(pdfUrl) {
        console.log("📥 Cargando PDF desde:", pdfUrl);
        
        if (typeof pdfjsLib === 'undefined') {
            console.error('PDF.js no está cargado');
            alert('Error: PDF.js no está disponible');
            return;
        }

        try {
            const loadingTask = pdfjsLib.getDocument(pdfUrl);
            this.state.pdfDoc = await loadingTask.promise;
            
            if (this.elements.pageCount) {
                this.elements.pageCount.textContent = this.state.pdfDoc.numPages;
            }
            
            this.state.pageNum = 1;
            
            // Calcular escala apropiada
            const page = await this.state.pdfDoc.getPage(1);
            const viewport = page.getViewport({ scale: 1 });
            const containerWidth = this.elements.canvas?.parentElement?.clientWidth || 800;
            this.state.scale = Math.min(1.5, (containerWidth - 100) / viewport.width);
            
            await this.renderPage(this.state.pageNum);
            
        } catch (error) {
            console.error('❌ Error al cargar PDF:', error);
            alert('Error al cargar el PDF. Intente descargarlo directamente.');
        }
    }

    async renderPage(num) {
        if (!this.state.pdfDoc || this.state.pageRendering) return;
        
        this.state.pageRendering = true;
        
        try {
            const page = await this.state.pdfDoc.getPage(num);
            const viewport = page.getViewport({ scale: this.state.scale });
            
            if (this.elements.canvas) {
                this.elements.canvas.height = viewport.height;
                this.elements.canvas.width = viewport.width;
                
                const renderContext = {
                    canvasContext: this.elements.ctx,
                    viewport: viewport
                };
                
                await page.render(renderContext).promise;
            }
            
            if (this.elements.pageNum) {
                this.elements.pageNum.textContent = num;
            }
            
            this.state.pageRendering = false;
            
            // Renderizar página pendiente si existe
            if (this.state.pageNumPending !== null) {
                this.renderPage(this.state.pageNumPending);
                this.state.pageNumPending = null;
            }
            
        } catch (error) {
            console.error('Error renderizando página:', error);
            this.state.pageRendering = false;
        }
    }

    queueRenderPage(num) {
        if (this.state.pageRendering) {
            this.state.pageNumPending = num;
        } else {
            this.renderPage(num);
        }
    }

    openPdfModal(pdfUrl, solicitudNumero) {
        if (!this.elements.pdfModal) {
            console.warn('Modal PDF no encontrado');
            return;
        }

        if (this.elements.modalSolicitudNumero) {
            this.elements.modalSolicitudNumero.textContent = solicitudNumero;
        }
        
        if (this.elements.downloadFromModal) {
            this.elements.downloadFromModal.href = pdfUrl;
            this.elements.downloadFromModal.download = `${solicitudNumero}.pdf`;
        }
        
        this.loadPdf(pdfUrl);
        this.elements.pdfModal.show();
    }

    // Table Functions
    updateTable() {
        const searchTerm = this.elements.search?.value.toLowerCase() || '';
        let visibleCount = 0;
        const items = [];
        
        this.elements.solicitudItems.forEach(item => {
            let matchesAll = true;
            
            // Búsqueda general
            if (searchTerm) {
                const numero = item.getAttribute('data-numero') || '';
                const descripcion = item.getAttribute('data-descripcion') || '';
                const matchesSearch = numero.includes(searchTerm) || 
                                    descripcion.includes(searchTerm);
                if (!matchesSearch) matchesAll = false;
            }
            
            // Filtros específicos
            if (this.config.filters) {
                this.config.filters.forEach(filter => {
                    const filterElement = this.elements[filter];
                    if (filterElement && filterElement.value) {
                        const itemValue = item.getAttribute(`data-${filter}`) || '';
                        if (itemValue !== filterElement.value) {
                            matchesAll = false;
                        }
                    }
                });
            }
            
            if (matchesAll) {
                items.push(item);
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        this.sortItems(items);
        
        if (this.elements.resultCount) {
            this.elements.resultCount.textContent = visibleCount;
        }
        
        if (this.elements.noResults) {
            const hasAnyItems = this.elements.solicitudItems.length > 0;
            this.elements.noResults.classList.toggle('d-none', visibleCount > 0 || !hasAnyItems);
        }
    }

    sortItems(items) {
        const priorityOrder = { 'alta': 3, 'media': 2, 'baja': 1 };
        const estadoOrder = { 
            'pendiente': 1, 
            'aprobada': 2, 
            'rechazada': 3, 
            'cotizacion': 4, 
            'completada': 5 
        };
        
        items.sort((a, b) => {
            let aValue, bValue;
            const sortField = this.state.currentSort.field;
            
            switch(sortField) {
                case 'numero':
                    aValue = a.getAttribute('data-numero') || '';
                    bValue = b.getAttribute('data-numero') || '';
                    break;
                case 'descripcion':
                    aValue = a.getAttribute('data-descripcion') || '';
                    bValue = b.getAttribute('data-descripcion') || '';
                    break;
                case 'prioridad':
                    aValue = priorityOrder[a.getAttribute('data-prioridad')] || 0;
                    bValue = priorityOrder[b.getAttribute('data-prioridad')] || 0;
                    break;
                case 'estado':
                    aValue = estadoOrder[a.getAttribute('data-estado')] || 0;
                    bValue = estadoOrder[b.getAttribute('data-estado')] || 0;
                    break;
                case 'fecha':
                default:
                    aValue = new Date(a.getAttribute('data-fecha') || 0);
                    bValue = new Date(b.getAttribute('data-fecha') || 0);
            }
            
            if (this.state.currentSort.direction === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });
        
        // Reordenar en el DOM
        const tbody = document.querySelector('#solicitudesTable tbody');
        if (tbody) {
            items.forEach(item => tbody.appendChild(item));
        }
    }

    setupEventListeners() {
        // Filtros comunes
        if (this.elements.search) {
            this.elements.search.addEventListener('input', () => this.updateTable());
        }

        // Filtros específicos
        if (this.config.filters) {
            this.config.filters.forEach(filter => {
                const filterElement = this.elements[filter];
                if (filterElement) {
                    filterElement.addEventListener('change', () => this.updateTable());
                }
            });
        }

        // Botones comunes
        if (this.elements.clearFilters) {
            this.elements.clearFilters.addEventListener('click', () => this.clearFilters());
        }

        if (this.elements.resetSearch) {
            this.elements.resetSearch.addEventListener('click', () => this.clearFilters());
        }

        // Ordenamiento
        this.elements.sortableHeaders.forEach(header => {
            header.addEventListener('click', () => this.handleSort(header));
        });

        // PDF Viewer - Usar delegación de eventos para elementos dinámicos
        document.addEventListener('click', (e) => {
            const pdfButton = e.target.closest('.view-pdf-btn');
            if (pdfButton) {
                e.preventDefault();
                this.openPdfModal(
                    pdfButton.getAttribute('data-pdf-url'),
                    pdfButton.getAttribute('data-solicitud-numero')
                );
            }
        });

        // Navegación PDF
        if (this.elements.prevPage) {
            this.elements.prevPage.addEventListener('click', () => {
                if (this.state.pageNum <= 1 || !this.state.pdfDoc) return;
                this.state.pageNum--;
                this.queueRenderPage(this.state.pageNum);
            });
        }

        if (this.elements.nextPage) {
            this.elements.nextPage.addEventListener('click', () => {
                if (!this.state.pdfDoc || this.state.pageNum >= this.state.pdfDoc.numPages) return;
                this.state.pageNum++;
                this.queueRenderPage(this.state.pageNum);
            });
        }

        // Limpiar modal PDF
        const pdfModalElement = document.getElementById('pdfModal');
        if (pdfModalElement) {
            pdfModalElement.addEventListener('hidden.bs.modal', () => {
                if (this.state.pdfDoc) {
                    this.state.pdfDoc.destroy();
                    this.state.pdfDoc = null;
                }
                if (this.elements.canvas) {
                    this.elements.canvas.width = 0;
                    this.elements.canvas.height = 0;
                }
                this.state.pageNum = 1;
                this.state.pageNumPending = null;
            });
        }
    }

    handleSort(header) {
        const field = header.getAttribute('data-sort');
        const icon = header.querySelector('i');
        
        // Resetear iconos de otros headers
        this.elements.sortableHeaders.forEach(h => {
            const otherIcon = h.querySelector('i');
            if (otherIcon && h !== header) {
                otherIcon.className = 'fas fa-sort ms-1';
            }
        });
        
        // Actualizar estado de ordenamiento
        if (this.state.currentSort.field === field) {
            this.state.currentSort.direction = this.state.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.currentSort.field = field;
            this.state.currentSort.direction = 'asc';
        }
        
        // Actualizar icono
        if (icon) {
            icon.className = this.state.currentSort.direction === 'asc' ? 
                'fas fa-sort-up ms-1' : 'fas fa-sort-down ms-1';
        }
        
        this.updateTable();
    }

    clearFilters() {
        if (this.elements.search) {
            this.elements.search.value = '';
        }
        
        if (this.config.filters) {
            this.config.filters.forEach(filter => {
                const filterElement = this.elements[filter];
                if (filterElement) {
                    filterElement.value = '';
                }
            });
        }
        
        this.updateTable();
    }
}