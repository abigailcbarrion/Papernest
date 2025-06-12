document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const elements = {
        country: document.getElementById('country'),
        province: document.getElementById('province'),
        city: document.getElementById('city'),
        barangay: document.getElementById('barangay'),
        postalCode: document.getElementById('postal_code'),
        password: document.getElementById('password')
    };

    // Initialize password toggles
    initializePasswordToggles();
    
    // Initialize address dropdowns
    initializeAddressHandlers();

    function initializePasswordToggles() {
        if (elements.password) createPasswordToggle(elements.password);
    }

    function createPasswordToggle(inputField) {
        const wrapper = createWrapper();
        const toggleBtn = createToggleButton();
        
        wrapInput(inputField, wrapper, toggleBtn);
        addToggleEventListener(inputField, toggleBtn);
    }

    function createWrapper() {
        const wrapper = document.createElement('div');
        Object.assign(wrapper.style, {
            position: 'relative',
            display: 'inline-block',
            width: '100%'
        });
        return wrapper;
    }

    function createToggleButton() {
        const toggleBtn = document.createElement('span');
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        Object.assign(toggleBtn.style, {
            position: 'absolute',
            right: '10px',
            top: '50%',
            transform: 'translateY(-50%)',
            cursor: 'pointer',
            color: '#666',
            fontSize: '16px'
        });
        return toggleBtn;
    }

    function wrapInput(inputField, wrapper, toggleBtn) {
        inputField.parentNode.insertBefore(wrapper, inputField);
        wrapper.appendChild(inputField);
        wrapper.appendChild(toggleBtn);
    }

    function addToggleEventListener(inputField, toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const isPassword = inputField.type === 'password';
            inputField.type = isPassword ? 'text' : 'password';
            toggleBtn.innerHTML = isPassword ? 
                '<i class="fas fa-eye-slash"></i>' : 
                '<i class="fas fa-eye"></i>';
        });
    }

    function initializeAddressHandlers() {
        if (elements.province) {
            elements.province.addEventListener('change', handleProvinceChange);
        }
        if (elements.city) {
            elements.city.addEventListener('change', handleCityChange);
        }
    }

    function handleProvinceChange() {
        const provinceCode = this.value;
        console.log('Province changed to:', provinceCode);
        
        resetDependentSelects();
        
        if (provinceCode && provinceCode !== 'void') {
            loadCities(provinceCode);
        }
    }

    function handleCityChange() {
        const cityCode = this.value;
        const cityName = this.options[this.selectedIndex].text;
        console.log('City changed to:', cityCode, cityName);
        
        resetSelect(elements.barangay, '--Select barangay--');
        
        if (cityCode && cityCode !== 'void') {
            updatePostalCode(cityName);
            loadBarangays(cityCode);
        } else {
            elements.postalCode.value = '';
        }
    }

    function resetDependentSelects() {
        if (elements.city) {
            resetSelect(elements.city, '--Select city--');
        }
        if (elements.barangay) {
            resetSelect(elements.barangay, '--Select barangay--');
        }
        if (elements.postalCode) {
            elements.postalCode.value = '';
        }
    }

    function resetSelect(selectElement, defaultText) {
        if (selectElement) {
            selectElement.innerHTML = `<option value="void">${defaultText}</option>`;
        }
    }

    function populateSelect(selectElement, options, defaultText) {
        if (!selectElement) {
            console.error('Select element is null');
            return;
        }
        
        resetSelect(selectElement, defaultText);
        
        if (options && Array.isArray(options)) {
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.code || option.value || '';
                optionElement.textContent = option.name || option.text || '';
                selectElement.appendChild(optionElement);
            });
            console.log(`Populated ${options.length} options in select`);
        } else {
            console.warn('No valid options provided to populate select');
        }
    }

    function showLoading(element, message) {
        if (element) {
            element.innerHTML = `<option value="void">${message}</option>`;
            element.disabled = true;
        }
    }

    function enableSelect(element) {
        if (element) {
            element.disabled = false;
        }
    }

    function loadCities(provinceCode) {
        console.log('Loading cities for province:', provinceCode);
        showLoading(elements.city, 'Loading cities...');
        
        fetchData(`/get_cities/${provinceCode}`)
            .then(data => {
                console.log('Cities response:', data);
                enableSelect(elements.city);
                if (data && data.cities) {
                    populateSelect(elements.city, data.cities, '--Select city--');
                } else {
                    handleLoadError(elements.city, 'No cities found');
                }
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                handleLoadError(elements.city, 'Error loading cities');
            });
    }

    function loadBarangays(cityCode) {
        console.log('Loading barangays for city:', cityCode);
        
        if (!cityCode || cityCode === 'void') {
            console.log('Invalid city code, skipping barangay load');
            return;
        }
        
        showLoading(elements.barangay, 'Loading barangays...');
        
        fetchData(`/get_barangays/${cityCode}`)
            .then(data => {
                console.log('Barangays response:', data);
                enableSelect(elements.barangay);
                if (data && data.barangays) {
                    if (data.barangays.length > 0) {
                        populateSelect(elements.barangay, data.barangays, '--Select barangay--');
                    } else {
                        elements.barangay.innerHTML = '<option value="void">No barangays found</option>';
                    }
                } else {
                    handleLoadError(elements.barangay, 'No barangays found');
                }
            })
            .catch(error => {
                console.error('Error loading barangays:', error);
                handleLoadError(elements.barangay, 'Error loading barangays');
            });
    }

    function updatePostalCode(cityName) {
        console.log('Updating postal code for city:', cityName);
        
        if (!cityName || cityName === 'void' || cityName === '--Select city--') {
            elements.postalCode.value = '';
            return;
        }

        setPostalCodeLoading();
        
        const encodedCityName = encodeURIComponent(cityName);
        const url = `/get_postal_code?country_code=PH&city=${encodedCityName}`;
        console.log('Fetching postal code from:', url);
        
        fetchData(url)
            .then(data => {
                console.log('Postal code response:', data);
                const postalCode = data.postal_code || '1000';
                setPostalCodeValue(postalCode);
            })
            .catch(error => {
                console.error('Error fetching postal code:', error);
                setPostalCodeValue('1000');
            });
    }

    function setPostalCodeLoading() {
        if (elements.postalCode) {
            elements.postalCode.value = 'Loading...';
            elements.postalCode.style.color = '#999';
        }
    }

    function setPostalCodeValue(value) {
        if (elements.postalCode) {
            elements.postalCode.value = value;
            elements.postalCode.style.color = '#000';
            console.log('Postal code set to:', value);
        }
    }

    function fetchData(url) {
        console.log('Fetching data from:', url);
        return fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Parsed data:', data);
                return data;
            });
    }

    function handleLoadError(element, errorMessage) {
        console.error('Load error:', errorMessage);
        enableSelect(element);
        if (element) {
            element.innerHTML = `<option value="void">${errorMessage}</option>`;
        }
    }

    // Check if all elements exist
    console.log('Element check:', {
        province: !!elements.province,
        city: !!elements.city,
        barangay: !!elements.barangay,
        postalCode: !!elements.postalCode
    });

    console.log('Registration form initialized');
});