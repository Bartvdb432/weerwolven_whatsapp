import pkg from 'whatsapp-web.js';
const { Client, LocalAuth } = pkg;
import qrcode from 'qrcode-terminal';
import express from 'express';
import axios from 'axios';
import { spawn } from 'child_process';
import path from 'path';
import schedule from 'node-schedule';

// ---------------------------
// Helper function to send bot messages with tagging
// ---------------------------
async function sendBotMessage(to, message, mentionsList = []) {
    try {
        const chat = await client.getChatById(to);

        // Match @digits optionally with @c.us
        const mentionPattern = /@(\d{5,15})(?:@c\.us)?/g;
        const mentionIds = [];
        let match;
        while ((match = mentionPattern.exec(message)) !== null) {
            let number = match[1];
            mentionIds.push(number + "@c.us"); // normalize
        }

        // Fetch contacts for mentions
        const mentions = [...mentionsList]; // start with pre-defined mentions from Python if any
        for (let id of mentionIds) {
            try {
                const contact = await client.getContactById(id);
                mentions.push(contact);
            } catch {
                console.warn(`⚠️ Could not get contact for ${id}`);
            }
        }

        // Replace numbers in text for readability
        message = message.replace(/@(\d{5,15})(?:@c\.us)?/g, '@$1');

        await chat.sendMessage(`🤖\n${message}`, { mentions });
        console.log(`📤 Sent message to ${to}: ${message}`);
    } catch (error) {
        console.error('⚠️ Failed to send message:', error);
    }
}

// ---------------------------
// 0. Start Python server automatically
// ---------------------------
const pythonScriptPath = path.join('.', 'server.py');
const pythonProcess = spawn('python', [pythonScriptPath], {
    env: { ...process.env, PYTHONUTF8: '1' },
    stdio: 'pipe'
});

pythonProcess.stdout.on('data', data => console.log(`🐍 Python: ${data.toString().trim()}`));
pythonProcess.stderr.on('data', data => console.error(`⚠️ Python error: ${data.toString().trim()}`));
pythonProcess.on('close', code => console.log(`🐍 Python process exited with code ${code}`));

// ---------------------------
// 1. Create WhatsApp client
// ---------------------------
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: '/usr/bin/chromium-browser',
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// ---------------------------
// 2. Express server
// ---------------------------
const app = express();
app.use(express.json());

app.post('/send', async (req, res) => {
    const { to, message } = req.body;
    if (!to || !message) return res.status(400).send('Missing parameters');
    try { await sendBotMessage(to, message); res.send('Message sent'); }
    catch (error) { console.error(error); res.status(500).send('Failed to send'); }
});

app.post('/fetch_messages', async (req, res) => {
    const { group_id, limit } = req.body;
    try {
        const chat = await client.getChatById(group_id);
        const messages = await chat.fetchMessages({ limit: limit || 2 });
        const simpleMessages = messages.map(m => ({
            from: m.author || m.from,
            body: m.body,
            timestamp: m.timestamp
        }));
        res.json(simpleMessages);
    } catch (err) { console.error(err); res.status(500).json({ error: err.message }); }
});

app.listen(3000, () => console.log('🌍 Node.js server running on port 3000'));

// ---------------------------
// 3. QR code login
// ---------------------------
client.on('qr', qr => qrcode.generate(qr, { small: true }));
client.on('ready', () => console.log('✅ WhatsApp connected and ready!'));

// ---------------------------
// 4. Polls and command handling
// ---------------------------
let pollPlayers = new Set();
let pollMessageId = null;
const processedMessages = new Set();

client.on('message_create', async msg => {
    const msgId = msg.id?._serialized;
    if (!msgId) return;
    if (processedMessages.has(msgId)) return;
    processedMessages.add(msgId);
    if (processedMessages.size > 1000) processedMessages.delete(processedMessages.values().next().value);

    const text = msg.body?.trim();
    if (!text?.startsWith('/')) return;

    const chat = await msg.getChat();
    const chatId = msg.from;
    const isGroup = chatId.endsWith('@g.us');
    const Group = chat.isGroup;

    let privateId = null;
    let groupSpecificId = msg.author || null;
    let groupId = Group ? chat.id._serialized : null;

    if (isGroup && msg.author) {
        const contact = await client.getContactById(msg.author);
        privateId = contact.number + "@c.us";
        groupSpecificId = msg.author.replace("@lid", "@c.us");
    } else {
        const contact = await client.getContactById(msg.from);
        privateId = contact.number + "@c.us";
        groupSpecificId = null;
    }

    console.log(`💬 Command received: ${text}`);
    console.log(`👤 Private ID: ${privateId}, Group-specific ID: ${groupSpecificId}, Group ID: ${groupId}`);

    // --- Forward all commands to Python ---
    try {
        const res = await axios.post('http://127.0.0.1:5000/process', {
            from: chatId,
            author: groupSpecificId,
            private_id: privateId,
            group_id: groupId,
            command: text
        });

        // ✅ Handle Python responses, including reactions
        if (Array.isArray(res.data)) {
            for (const item of res.data) {
                if (item.reply) await sendBotMessage(chatId, item.reply);
                if (item.react) await msg.react(item.react); // React if Python says so
            }
        } else {
            if (res.data?.reply) await sendBotMessage(chatId, res.data.reply);
            if (res.data?.react) await msg.react(res.data.react); // React if Python says so
        }

    } catch (err) {
        console.error('⚠️ Error contacting Python server:', err.message);
    }
});

// ---------------------------
// 5. Reaction tracking
// ---------------------------
client.on('message_reaction', async reaction => {
    const reactionMessageId = reaction.message?.id?._serialized;
    if (!reactionMessageId || !pollMessageId) return;
    if (reactionMessageId !== pollMessageId) return;

    const user = await reaction.getUser();
    const nameOrNumber = user.pushname || user.number;
    pollPlayers.add(nameOrNumber);
    console.log(`✅ ${nameOrNumber} joined the game`);
});

// ---------------------------
// 6. Start WhatsApp client
// ---------------------------
client.initialize();