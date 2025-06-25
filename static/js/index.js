/**
 * 主前端应用文件
 * 使用模块化架构重构
 */

// API客户端类
class APIClient {
    constructor() {
        this.baseURL = '/api';
    }

    async request(endpoint, data = null, method = 'GET') {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}`);
            }
            
            return result;
        } catch (error) {
            console.error(`API请求失败 [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    // 分析服务API
    async analyzeTraffic(httpData) {
        return this.request('/analyze_traffic', { http_data: httpData }, 'POST');
    }

    async decode(encodedStr) {
        return this.request('/decode', { encoded_str: encodedStr }, 'POST');
    }

    async auditJS(jsCode) {
        return this.request('/audit_js', { js_code: jsCode }, 'POST');
    }

    async analyzeProcess(processData) {
        return this.request('/analyze_process', { process_data: processData }, 'POST');
    }

    async generateRegex(sourceText, targetText) {
        return this.request('/generate_regex', { 
            source_text: sourceText, 
            target_text: targetText 
        }, 'POST');
    }

    async analyzeWebshell(fileContent, fileName = '') {
        return this.request('/detect_webshell', { 
            file_content: fileContent, 
            file_name: fileName 
        }, 'POST');
    }

    async analyzeWeblog(logContent, analysisTypes) {
        return this.request('/analyze_weblog', { 
            log_content: logContent, 
            analysis_types: analysisTypes 
        }, 'POST');
    }

    async chatWeblog(question, logContent, analysisResult) {
        return this.request('/chat_weblog', {
            question: question,
            log_content: logContent,
            analysis_result: analysisResult
        }, 'POST');
    }

    async translate(text, sourceLang, targetLang) {
        return this.request('/translate', { 
            text, 
            source_lang: sourceLang,
            target_lang: targetLang 
        }, 'POST');
    }

    // 配置管理API
    async getConfig() {
        return this.request('/get_config');
    }

    async saveConfig(config) {
        return this.request('/save_config', config, 'POST');
    }

    async testConfig(config) {
        return this.request('/test_config', config, 'POST');
    }

    async validateConfig() {
        return this.request('/validate_config');
    }

    async resetConfig() {
        return this.request('/reset_config', {}, 'POST');
    }
}

// UI管理器类
class UIManager {
    constructor() {
        this.domCache = {};
        this.fileInputs = {};
        this.loadingContainer = null;
        this.init();
    }

    init() {
        this.cacheElements();
        this.initFileInputs();
        this.initTheme();
        this.initTabs();
        this.initLoading();
        this.bindEvents();
    }

    cacheElements() {
        this.domCache = {
            themeSelect: document.getElementById('theme'),
            navItems: document.querySelectorAll('.nav-item'),
            tabContents: document.querySelectorAll('.tab-content'),
            sidebarToggle: document.querySelector('.sidebar-toggle'),
            sidebar: document.querySelector('.sidebar')
        };
    }

    initFileInputs() {
        const inputConfigs = {
            'choose-file': { type: 'file' },
            'choose-dir': { type: 'file', webkitdirectory: true },
            'choose-log-file': { type: 'file', accept: '.log,.txt,.access,.error' }
        };

        Object.entries(inputConfigs).forEach(([buttonId, config]) => {
            const input = document.createElement('input');
            input.type = config.type;
            if (config.webkitdirectory) input.webkitdirectory = true;
            if (config.accept) input.accept = config.accept;
            input.style.display = 'none';
            document.body.appendChild(input);
            this.fileInputs[buttonId] = input;
        });
    }

    initTheme() {
        if (!this.domCache.themeSelect) return;

        const savedTheme = localStorage.getItem('theme') || '浅色主题';
        this.domCache.themeSelect.value = savedTheme;
        this.setTheme(savedTheme);

        this.domCache.themeSelect.addEventListener('change', (e) => {
            this.setTheme(e.target.value);
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    initTabs() {
        if (!this.domCache.navItems.length) return;

        this.domCache.navItems.forEach(item => {
            item.addEventListener('click', () => this.switchTab(item));
        });

        // 初始化侧边栏切换
        if (this.domCache.sidebarToggle) {
            this.domCache.sidebarToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // 默认激活第一个标签页
        if (this.domCache.navItems.length > 0) {
            this.switchTab(this.domCache.navItems[0]);
        }
    }

    switchTab(activeItem) {
        const tabId = activeItem.getAttribute('data-tab');

        // 更新导航项状态
        this.domCache.navItems.forEach(item => item.classList.remove('active'));
        activeItem.classList.add('active');

        // 更新内容显示
        this.domCache.tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === tabId) {
                content.classList.add('active');
            }
        });
    }

    toggleSidebar() {
        if (this.domCache.sidebar) {
            this.domCache.sidebar.classList.toggle('collapsed');
        }
    }

    initLoading() {
        this.addLoadingStyles();
        this.createLoadingContainer();
    }

    addLoadingStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .loading-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.8);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                z-index: 1000;
                display: none;
            }
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            .loading-text {
                color: white;
                margin-bottom: 10px;
                font-size: 16px;
            }
            .loading-progress {
                width: 200px;
                height: 4px;
                background: #f3f3f3;
                border-radius: 2px;
                overflow: hidden;
            }
            .progress-bar {
                width: 0%;
                height: 100%;
                background: #3498db;
                transition: width 0.3s ease;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .button-loading {
                position: relative;
                pointer-events: none;
                opacity: 0.7;
            }
            .button-loading::after {
                content: '';
                position: absolute;
                width: 20px;
                height: 20px;
                top: 50%;
                left: 50%;
                margin: -10px 0 0 -10px;
                border: 2px solid #fff;
                border-top-color: transparent;
                border-radius: 50%;
                animation: button-spin 1s linear infinite;
            }
            @keyframes button-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    createLoadingContainer() {
        this.loadingContainer = document.createElement('div');
        this.loadingContainer.className = 'loading-container';
        this.loadingContainer.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">正在处理中...</div>
            <div class="loading-progress">
                <div class="progress-bar"></div>
            </div>
        `;
        document.body.appendChild(this.loadingContainer);
    }

    showLoading(text = '正在处理中...') {
        const textElement = this.loadingContainer.querySelector('.loading-text');
        textElement.textContent = text;
        this.loadingContainer.style.display = 'block';
    }

    hideLoading() {
        this.loadingContainer.style.display = 'none';
    }

    updateProgress(progress) {
        const progressBar = this.loadingContainer.querySelector('.progress-bar');
        progressBar.style.width = `${progress}%`;
    }

    setButtonLoading(buttonId, isLoading) {
        const button = document.getElementById(buttonId);
        if (button) {
            if (isLoading) {
                button.classList.add('button-loading');
                button.disabled = true;
            } else {
                button.classList.remove('button-loading');
                button.disabled = false;
            }
        }
    }

    showResult(elementId, data) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = data;
            element.style.display = 'block';
            element.style.color = '';
        }
    }

    showError(elementId, error) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `错误: ${error}`;
            element.style.display = 'block';
            element.style.color = 'var(--error-color)';
        }
    }

    bindEvents() {
        this.bindFileEvents();
        // 绑定窗口大小变化事件
        window.addEventListener('resize', () => {
            this.handleResize();
            // 调整聊天容器高度
            setTimeout(() => {
                if (this.adjustChatContainerHeight) {
                    this.adjustChatContainerHeight();
                }
            }, 200);
        });
    }

    handleResize() {
        // 处理窗口大小变化
        const sidebar = this.domCache.sidebar;
        if (sidebar && window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
        }
    }

    bindFileEvents() {
        // 文件选择按钮事件
        Object.keys(this.fileInputs).forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', () => {
                    this.fileInputs[buttonId].click();
                });
            }
        });

        // 文件选择事件
        Object.keys(this.fileInputs).forEach(buttonId => {
            this.fileInputs[buttonId].addEventListener('change', (e) => {
                this.handleFileSelection(buttonId, e.target.files);
            });
        });
    }

    handleFileSelection(buttonId, files) {
        const filesArray = Array.from(files);
        if (filesArray.length > 0) {
            const fileNames = filesArray.map(f => f.name).join(', ');
            const button = document.getElementById(buttonId);
            if (button) {
                button.textContent = `已选择 ${filesArray.length} 个文件`;
                button.title = fileNames;
            }

            // 特殊处理日志文件读取
            if (buttonId === 'choose-log-file' && filesArray[0]) {
                this.handleLogFileRead(filesArray[0]);
            }
        }
    }

    handleLogFileRead(file) {
        const pathSpan = document.getElementById('log-file-path');
        const textarea = document.getElementById('weblog-input');

        if (pathSpan) {
            pathSpan.textContent = file.name;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            if (textarea) {
                textarea.value = e.target.result;
            }
        };
        reader.onerror = () => {
            this.showError('weblog-result', '文件读取失败，请重试');
        };
        reader.readAsText(file, 'UTF-8');
    }
}

// 应用控制器类
class AppController {
    constructor() {
        this.apiClient = new APIClient();
        this.uiManager = new UIManager();
        this.init();
    }

    init() {
        this.bindAnalysisButtons();
        this.bindConfigButtons();
    }

    bindAnalysisButtons() {
        const buttonConfigs = [
            {
                buttonId: 'analyze-btn',
                inputId: 'traffic-input',
                resultId: 'traffic-result',
                emptyMessage: '请输入HTTP请求数据',
                loadingMessage: '正在分析网络流量...',
                apiMethod: 'analyzeTraffic'
            },
            {
                buttonId: 'decode-btn',
                inputId: 'decode-input',
                resultId: 'decode-result',
                emptyMessage: '请输入需要解码的字符串',
                loadingMessage: '正在解码中...',
                apiMethod: 'decode'
            },
            {
                buttonId: 'js-audit-btn',
                inputId: 'js-input',
                resultId: 'js-result',
                emptyMessage: '请输入JavaScript代码',
                loadingMessage: '正在审计JavaScript代码...',
                apiMethod: 'auditJS'
            },
            {
                buttonId: 'process-btn',
                inputId: 'process-input',
                resultId: 'process-result',
                emptyMessage: '请输入进程信息',
                loadingMessage: '正在分析进程信息...',
                apiMethod: 'analyzeProcess'
            },
            {
                buttonId: 'regex-btn',
                inputId: 'regex-input',
                resultId: 'regex-result',
                emptyMessage: '请输入需求描述',
                loadingMessage: '正在生成正则表达式...',
                apiMethod: 'generateRegex'
            },
            {
                buttonId: 'webshell-btn',
                inputId: 'webshell-input',
                resultId: 'webshell-result',
                emptyMessage: '请输入代码内容',
                loadingMessage: '正在检测WebShell...',
                apiMethod: 'analyzeWebshell'
            }
        ];

        buttonConfigs.forEach(config => {
            this.bindAnalysisButton(config);
        });

        // 特殊处理的按钮
        this.bindWeblogButton();
        this.initTranslation();
    }

    bindAnalysisButton(config) {
        const button = document.getElementById(config.buttonId);
        if (!button) return;

        button.addEventListener('click', async () => {
            const input = document.getElementById(config.inputId).value.trim();
            if (!input) {
                this.uiManager.showError(config.resultId, config.emptyMessage);
                return;
            }

            await this.executeAnalysis(
                config.buttonId,
                config.resultId,
                config.loadingMessage,
                () => this.apiClient[config.apiMethod](input)
            );
        });
    }

    bindWeblogButton() {
        const button = document.getElementById('weblog-analyze-btn');
        if (!button) return;

        button.addEventListener('click', async () => {
            const input = document.getElementById('weblog-input').value.trim();
            if (!input) {
                this.uiManager.showError('weblog-result', '请输入Web日志内容或选择日志文件');
                return;
            }

            const analysisTypes = [];
            const checkboxes = [
                { id: 'check-attack', type: '攻击检测' },
                { id: 'check-anomaly', type: '异常行为' },
                { id: 'check-statistics', type: '访问统计' },
                { id: 'check-performance', type: '性能分析' }
            ];

            checkboxes.forEach(checkbox => {
                const element = document.getElementById(checkbox.id);
                if (element && element.checked) {
                    analysisTypes.push(checkbox.type);
                }
            });

            const result = await this.executeAnalysis(
                'weblog-analyze-btn',
                'weblog-result',
                '正在分析Web日志...',
                () => this.apiClient.analyzeWeblog(input, analysisTypes)
            );
            
            // 分析完成后显示对话功能
            if (result) {
                this.showWeblogChat();
                // 保存分析结果和日志内容用于对话
                this.weblogAnalysisResult = result;
                this.weblogContent = input;
            }
        });
        
        // 绑定对话功能
        this.bindWeblogChatEvents();
    }

    detectLanguage(text) {
        // 简单的语言检测，检查是否包含中文字符
        const chineseRegex = /[\u4e00-\u9fff]/;
        return chineseRegex.test(text) ? 'zh' : 'en';
    }

    initTranslation() {
        // 查找翻译按钮，可能在HTML中定义为onclick
        const button = document.querySelector('button[onclick="translateText()"]');
        if (!button) return;

        // 移除原有的onclick属性，使用事件监听器
        button.removeAttribute('onclick');
        button.addEventListener('click', async () => {
            const input = document.getElementById('translation-input').value.trim();
            const targetLang = document.getElementById('target-language').value;
            
            if (!input) {
                this.uiManager.showError('translate-result', '请输入需要翻译的文本');
                return;
            }

            // 自动检测源语言，默认为中文
            const sourceLang = this.detectLanguage(input);

            await this.executeAnalysis(
                'translate-btn',
                'translate-result',
                '正在翻译中...',
                () => this.apiClient.translate(input, sourceLang, targetLang)
            );
        });
    }

    async executeAnalysis(buttonId, resultId, loadingMessage, apiCall) {
        this.uiManager.setButtonLoading(buttonId, true);
        this.uiManager.showLoading(loadingMessage);
        this.uiManager.updateProgress(0);

        try {
            const result = await apiCall();
            this.uiManager.showResult(resultId, result.result);
            this.uiManager.updateProgress(100);
            return result; // 返回分析结果
        } catch (error) {
            this.uiManager.showError(resultId, error.message);
            return null; // 错误时返回null
        } finally {
            this.uiManager.setButtonLoading(buttonId, false);
            this.uiManager.hideLoading();
        }
    }

    bindConfigButtons() {
        // API类型切换
        const apiTypeSelect = document.getElementById('api-type');
        if (apiTypeSelect) {
            apiTypeSelect.addEventListener('change', () => this.handleApiTypeChange());
            this.handleApiTypeChange(); // 初始化显示
        }

        // 配置管理按钮
        const configButtons = [
            { id: 'load-config-btn', handler: () => this.loadConfig() },
            { id: 'save-config-btn', handler: () => this.saveConfig() },
            { id: 'test-config-btn', handler: () => this.testConfig() },
            { id: 'validate-config-btn', handler: () => this.validateConfig() },
            { id: 'reset-config-btn', handler: () => this.resetConfig() }
        ];

        configButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            }
        });
    }

    handleApiTypeChange() {
        const apiType = document.getElementById('api-type').value;
        const configGroups = {
            'deepseek': document.getElementById('deepseek-config'),
            'openrouter': document.getElementById('openrouter-config'),
            'ollama': document.getElementById('ollama-config')
        };

        // 隐藏所有配置组
        Object.values(configGroups).forEach(group => {
            if (group) group.classList.add('hidden');
        });

        // 显示当前选中的配置组
        if (configGroups[apiType]) {
            configGroups[apiType].classList.remove('hidden');
        }
    }

    async loadConfig() {
        await this.executeConfigAction(
            'load-config-btn',
            '正在加载配置...',
            async () => {
                const result = await this.apiClient.getConfig();
                this.populateConfigForm(result.config);
                return '配置加载成功';
            }
        );
    }

    async saveConfig() {
        const configData = this.collectConfigData();
        await this.executeConfigAction(
            'save-config-btn',
            '正在保存配置...',
            async () => {
                const result = await this.apiClient.saveConfig(configData);
                return result.result;
            }
        );
    }

    async testConfig() {
        const configData = this.collectConfigData();
        
        // 转换为后端期望的格式
        const apiType = configData.api?.type;
        if (!apiType) {
            throw new Error('请选择API类型');
        }
        
        const apiConfig = configData[apiType];
        if (!apiConfig) {
            throw new Error(`请配置${apiType}的相关参数`);
        }
        
        const testData = {
            api_type: apiType,
            api_url: apiConfig.api_url || '',
            api_key: apiConfig.api_key || '',
            model: apiConfig.model || ''
        };
        
        await this.executeConfigAction(
            'test-config-btn',
            '正在测试连接...',
            async () => {
                const result = await this.apiClient.testConfig(testData);
                return result.result || result.message;
            }
        );
    }

    async validateConfig() {
        await this.executeConfigAction(
            'validate-config-btn',
            '正在验证配置...',
            async () => {
                const result = await this.apiClient.validateConfig();
                if (result.valid) {
                    return '配置验证通过';
                } else {
                    throw new Error(`配置验证失败: ${result.errors.join(', ')}`);
                }
            }
        );
    }

    async resetConfig() {
        if (!confirm('确定要重置配置为默认值吗？此操作不可撤销。')) {
            return;
        }

        await this.executeConfigAction(
            'reset-config-btn',
            '正在重置配置...',
            async () => {
                const result = await this.apiClient.resetConfig();
                // 重新加载配置表单
                setTimeout(() => this.loadConfig(), 1000);
                return result.result;
            }
        );
    }

    async executeConfigAction(buttonId, loadingMessage, action) {
        this.uiManager.setButtonLoading(buttonId, true);
        this.uiManager.showLoading(loadingMessage);

        try {
            const message = await action();
            this.uiManager.showResult('config-result', message);
        } catch (error) {
            this.uiManager.showError('config-result', error.message);
        } finally {
            this.uiManager.setButtonLoading(buttonId, false);
            this.uiManager.hideLoading();
        }
    }

    populateConfigForm(config) {
        // 设置API类型
        const apiTypeSelect = document.getElementById('api-type');
        if (apiTypeSelect && config.api && config.api.type) {
            apiTypeSelect.value = config.api.type;
            this.handleApiTypeChange();
        }

        // 填充各API配置
        const apiConfigs = {
            deepseek: ['url', 'key', 'model'],
            openrouter: ['url', 'key', 'model'],
            ollama: ['url', 'model']
        };

        Object.entries(apiConfigs).forEach(([apiType, fields]) => {
            if (config[apiType]) {
                fields.forEach(field => {
                    const element = document.getElementById(`${apiType}-${field}`);
                    const configKey = field === 'url' ? 'api_url' : 
                                     field === 'key' ? 'api_key' : field;
                    if (element && config[apiType][configKey]) {
                        element.value = config[apiType][configKey];
                    }
                });
            }
        });
    }

    collectConfigData() {
        const apiType = document.getElementById('api-type').value;
        const config = {
            api: { type: apiType }
        };

        // 收集各API配置
        const apiConfigs = {
            deepseek: ['url', 'key', 'model'],
            openrouter: ['url', 'key', 'model'],
            ollama: ['url', 'model']
        };

        Object.entries(apiConfigs).forEach(([api, fields]) => {
            const apiConfig = {};
            fields.forEach(field => {
                const element = document.getElementById(`${api}-${field}`);
                if (element && element.value.trim()) {
                    const configKey = field === 'url' ? 'api_url' : 
                                     field === 'key' ? 'api_key' : field;
                    apiConfig[configKey] = element.value.trim();
                }
            });
            if (Object.keys(apiConfig).length > 0) {
                config[api] = apiConfig;
            }
        });

        return config;
    }
    
    // Web日志对话功能
    showWeblogChat() {
        const chatMessages = document.getElementById('weblog-chat-messages');
        if (chatMessages) {
            // 找到包含智能对话的卡片容器
            const chatContainer = chatMessages.closest('.card');
            if (chatContainer) {
                chatContainer.style.display = 'block';
                chatContainer.scrollIntoView({ behavior: 'smooth' });
                
                // 重新绑定事件，确保按钮可以正常工作
                setTimeout(() => {
                    this.bindWeblogChatEvents();
                    this.adjustChatContainerHeight();
                }, 100);
            }
        }
    }
    
    bindWeblogChatEvents() {
        const sendButton = document.getElementById('weblog-chat-send');
        const clearButton = document.getElementById('weblog-chat-clear');
        const chatInput = document.getElementById('weblog-chat-input');
        
        console.log('绑定Web日志对话事件:', {
            sendButton: !!sendButton,
            clearButton: !!clearButton,
            chatInput: !!chatInput
        });
        
        if (sendButton) {
            // 添加测试点击事件
            sendButton.addEventListener('click', (e) => {
                console.log('发送按钮被点击', e);
                e.preventDefault();
                e.stopPropagation();
                this.sendWeblogChatMessage();
            });
            
            // 添加鼠标事件测试
            sendButton.addEventListener('mousedown', () => {
                console.log('发送按钮鼠标按下');
            });
        } else {
            console.error('未找到发送按钮元素');
        }
        
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearWeblogChat());
        }
        
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendWeblogChatMessage();
                }
            });
        }
    }
    
    async sendWeblogChatMessage() {
        console.log('sendWeblogChatMessage 方法被调用');
        const chatInput = document.getElementById('weblog-chat-input');
        const question = chatInput.value.trim();
        
        console.log('输入内容:', question);
        console.log('分析结果存在:', !!this.weblogAnalysisResult);
        console.log('日志内容存在:', !!this.weblogContent);
        
        if (!question) {
            this.uiManager.showError('weblog-chat-messages', '请输入您的问题');
            return;
        }
        
        if (!this.weblogAnalysisResult || !this.weblogContent) {
            this.uiManager.showError('weblog-chat-messages', '请先进行日志分析');
            return;
        }
        
        // 显示用户消息
        this.addChatMessage('user', question);
        chatInput.value = '';
        
        // 显示加载状态
        const loadingId = this.addChatMessage('assistant', '正在思考中...');
        
        try {
            const response = await this.apiClient.chatWeblog(
                question, 
                this.weblogContent, 
                this.weblogAnalysisResult
            );
            
            // 移除加载消息并显示回复
            this.removeChatMessage(loadingId);
            this.addChatMessage('assistant', response.result || response.answer || '抱歉，无法获取回复');
            
        } catch (error) {
            this.removeChatMessage(loadingId);
            
            // 提供更详细的错误信息
            let errorMessage = '抱歉，处理您的问题时遇到了问题。';
            
            if (error.message) {
                if (error.message.includes('内部服务器错误')) {
                    errorMessage = '服务器处理出现问题，可能的原因：\n' +
                                 '• AI服务暂时不可用\n' +
                                 '• 网络连接问题\n' +
                                 '• 请稍后重试或检查网络连接';
                } else if (error.message.includes('验证')) {
                    errorMessage = `输入验证失败：${error.message}`;
                } else if (error.message.includes('token') || error.message.includes('超限')) {
                    errorMessage = '文本内容过长，请尝试：\n' +
                                 '• 缩短您的问题\n' +
                                 '• 分批处理日志内容\n' +
                                 '• 联系管理员调整配置';
                } else {
                    errorMessage = `错误：${error.message}`;
                }
            }
            
            this.addChatMessage('assistant', errorMessage);
        }
    }
    
    addChatMessage(role, content) {
        const chatMessages = document.getElementById('weblog-chat-messages');
        if (!chatMessages) return;
        
        const messageId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        messageDiv.id = messageId;
        
        const roleSpan = document.createElement('div');
        roleSpan.className = 'message-role';
        roleSpan.textContent = role === 'user' ? '您' : 'AI助手';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(roleSpan);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // 平滑滚动到底部
        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
        
        // 动态调整聊天容器高度
        this.adjustChatContainerHeight();
        
        return messageId;
    }
    
    adjustChatContainerHeight() {
        const chatMessages = document.getElementById('weblog-chat-messages');
        const chatContainer = chatMessages?.closest('.chat-container');
        
        if (!chatMessages || !chatContainer) return;
        
        // 计算内容高度
        const messagesHeight = chatMessages.scrollHeight;
        const minHeight = 300;
        const maxHeight = Math.min(window.innerHeight * 0.7, 800);
        
        // 动态调整高度
        const newHeight = Math.max(minHeight, Math.min(messagesHeight + 100, maxHeight));
        chatContainer.style.height = newHeight + 'px';
        
        // 调整消息容器高度
        const inputContainer = chatContainer.querySelector('.chat-input-container');
        const chatActions = chatContainer.querySelector('.chat-actions');
        const reservedHeight = (inputContainer?.offsetHeight || 60) + (chatActions?.offsetHeight || 40) + 30;
        
        chatMessages.style.height = (newHeight - reservedHeight) + 'px';
    }
    
    removeChatMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
            this.adjustChatContainerHeight();
        }
    }
    
    clearWeblogChat() {
        const chatMessages = document.getElementById('weblog-chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
    }
}

// 全局函数
function handleApiTypeChange() {
    const apiType = document.getElementById('api-type').value;
    const configs = ['deepseek-config', 'openrouter-config', 'ollama-config'];
    
    configs.forEach(configId => {
        const element = document.getElementById(configId);
        if (element) {
            element.style.display = configId === `${apiType}-config` ? 'block' : 'none';
        }
    });
}

// 全局应用实例
let app;

// 全局函数，供HTML onclick使用
window.analyzeWeblog = async function() {
    if (app) {
        const input = document.getElementById('weblog-input');
        const analysisTypes = [];
        document.querySelectorAll('input[name="analysis-type"]:checked').forEach(cb => {
            analysisTypes.push(cb.value);
        });
        
        if (!input.value.trim()) {
            alert('请输入日志内容');
            return;
        }
        
        try {
            const result = await app.executeAnalysis(
                'analyze-weblog-btn',
                'weblog-result',
                '正在分析日志...',
                () => app.apiClient.analyzeWeblog(input.value, analysisTypes)
            );
            
            // 保存分析结果供对话功能使用
            if (result) {
                app.weblogContent = input.value;
                app.weblogAnalysisResult = result.result || result;
            }
        } catch (error) {
            console.error('日志分析失败:', error);
        }
    }
};

window.chatWeblog = function() {
    if (app) {
        // 首先切换到weblog-analysis tab
        const weblogTab = document.querySelector('[data-tab="weblog-analysis"]');
        if (weblogTab) {
            app.switchTab(weblogTab);
        }
        
        // 显示智能对话卡片
        app.showWeblogChat();
        
        // 如果有输入内容，则发送消息
        const question = document.getElementById('weblog-chat-input');
        if (question && question.value.trim()) {
            app.sendWeblogChatMessage();
        }
    }
};

window.clearWeblogInput = function() {
    const input = document.getElementById('weblog-input');
    if (input) input.value = '';
    const result = document.getElementById('weblog-result');
    if (result) result.innerHTML = '';
};

window.translateText = function() {
    // 这个函数已经通过事件监听器处理
};

window.clearTranslationInput = function() {
    const input = document.getElementById('translation-input');
    if (input) input.value = '';
    const result = document.getElementById('translate-result');
    if (result) result.innerHTML = '';
};

// 应用初始化
document.addEventListener('DOMContentLoaded', () => {
    try {
        app = new AppController();
        console.log('应用初始化成功');
        
        // 额外的事件绑定检查和备用绑定
        setTimeout(() => {
            const sendButton = document.getElementById('weblog-chat-send');
            if (sendButton) {
                console.log('发送按钮元素存在，样式:', window.getComputedStyle(sendButton));
                console.log('按钮是否可见:', sendButton.offsetWidth > 0 && sendButton.offsetHeight > 0);
                console.log('按钮位置:', sendButton.getBoundingClientRect());
                
                // 备用事件绑定 - 使用事件委托
                document.addEventListener('click', (e) => {
                    if (e.target.id === 'weblog-chat-send' || e.target.closest('#weblog-chat-send')) {
                        console.log('通过事件委托检测到发送按钮点击');
                        e.preventDefault();
                        e.stopPropagation();
                        if (app && app.sendWeblogChatMessage) {
                            app.sendWeblogChatMessage();
                        }
                    }
                });
                
            } else {
                console.error('页面加载完成后仍未找到发送按钮');
            }
        }, 1000);
        
    } catch (error) {
         console.error('应用初始化失败:', error);
     }
});