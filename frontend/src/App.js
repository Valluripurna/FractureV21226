import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import Login from './components/Login';
import Signup from './components/Signup';
import History from './components/History';
import './App.css';

// Import icons
import { FiUploadCloud, FiAlertTriangle, FiCheckCircle, FiMessageSquare, FiDownload, FiLogOut, FiUser, FiX, FiSend, FiFileText, FiPlus, FiHeart, FiClock, FiActivity, FiMapPin, FiSearch, FiVolume2 } from 'react-icons/fi';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [isDragging, setIsDragging] = useState(false);
  const [nearbyHospitals, setNearbyHospitals] = useState([]);
  const [showHospitalsModal, setShowHospitalsModal] = useState(false);
  const [showLocationPermissionModal, setShowLocationPermissionModal] = useState(false);
  const [showOutputs, setShowOutputs] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [analyticsError, setAnalyticsError] = useState('');
  const fileInputRef = useRef(null);
  const chatMessagesRef = useRef(null);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      console.log('Hash changed to:', hash);
      if (['signup', 'login', 'history', 'app'].includes(hash)) {
        setCurrentView(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const getMetricsSlug = () => {
    if (!result || !result.model_version) return 'efficientnet';
    const mv = String(result.model_version).toLowerCase();
    if (mv.includes('efficientnet')) return 'efficientnet';
    if (mv.includes('densenet121')) return 'densenet121';
    if (mv.includes('densenet169') || mv.includes('mura')) return 'densenet169';
    if (mv.includes('resnet50')) return 'resnet50';
    return 'efficientnet';
  };

  const loadImageAsDataUrl = (url) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function () {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0);
          const dataUrl = canvas.toDataURL('image/png');
          resolve(dataUrl);
        } catch (e) {
          resolve(null);
        }
      };
      img.onerror = () => resolve(null);
      img.src = url;
    });
  };

  const fetchMetricsImagesForPDF = async () => {
    const slug = getMetricsSlug();
    const baseUrl = 'http://localhost:5000/metrics';
    const [curves, cm, roc] = await Promise.all([
      loadImageAsDataUrl(`${baseUrl}/${slug}_training_curves.png`),
      loadImageAsDataUrl(`${baseUrl}/${slug}_confusion_matrix.png`),
      loadImageAsDataUrl(`${baseUrl}/${slug}_roc_curve.png`),
    ]);
    return { slug, curves, cm, roc };
  };

  const handleLoginSuccess = (userData) => {
    console.log('Login successful, setting user data:', userData);
    setUser(userData);
    setCurrentView('app');
    window.location.hash = '';
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setResult(null);
    setFile(null);
    setPreview(null);
    setCurrentView('login');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const processFile = (file) => {
    setFile(file);
    setResult(null);
    setError('');
    setShowChat(false);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      processFile(droppedFile);
    } else {
      setError('Please upload an image file (JPEG, PNG, BMP, TIFF)');
    }
  };

  const handleUploadAnother = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
    setShowChat(false);
    setShowOutputs(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const speakResult = (language = 'en') => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Voice is not supported in this browser.');
      return;
    }
    if (!result) return;

    const synth = window.speechSynthesis;
    synth.cancel();

    let text = '';
    if (language === 'te') {
      // Clear Telugu sentence for screen reader voices
      if (result.fracture_detected) {
        text = `ఈ ఎక్స్ రే విశ్లేషణలో ఎముక విరుగు ఉన్నట్టు కనిపిస్తోంది.
నమ్మకం శాతం సుమారు ${(result.confidence * 100).toFixed(0)} శాతం.`;
      } else {
        text = `ఈ ఎక్స్ రే విశ్లేషణలో ఎముక విరుగు కనిపించలేదు.
నమ్మకం శాతం సుమారు ${(result.confidence * 100).toFixed(0)} శాతం.`;
      }
    } else {
      if (result.fracture_detected) {
        text = `Fracture detected with about ${(result.confidence * 100).toFixed(0)} percent confidence.`;
      } else {
        text = `No fracture detected. Confidence is about ${(result.confidence * 100).toFixed(0)} percent.`;
      }
    }

    const utter = new SpeechSynthesisUtterance(text);
    const voices = synth.getVoices();
    const langPrefix = language === 'te' ? 'te' : 'en';
    const voiceMatch = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(langPrefix));
    if (voiceMatch) {
      utter.voice = voiceMatch;
    }
    utter.lang = language === 'te' ? 'te-IN' : 'en-IN';
    synth.speak(utter);
  };

  const handleDownloadPDF = async () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const genAt = new Date();
    const reportId = `FD-${genAt.getHours()}${genAt.getMinutes()}${genAt.getSeconds()}${genAt.getMilliseconds()}`;
    doc.setProperties({ title: 'FractureDetect AI Report' });

    // Color palette and helpers
    const colors = {
      header: [41, 128, 185],
      patient: [34, 197, 94],
      results: [59, 130, 246],
      recs: [244, 114, 182],
      hospitals: [99, 102, 241],
      disclaimer: [100, 100, 100],
    };
    const sectionBar = (title, color, yPos) => {
      doc.setFillColor(255, 255, 255);
      doc.setDrawColor(color[0], color[1], color[2]);
      doc.setLineWidth(0.4);
      doc.rect(10, yPos, 190, 10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(color[0], color[1], color[2]);
      doc.setFontSize(13);
      doc.text(title, 14, yPos + 7);
      doc.setDrawColor(220, 220, 220);
      doc.line(10, yPos + 11, 200, yPos + 11);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(0, 0, 0);
      return yPos + 16;
    };

    // Cover / header block
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
    doc.rect(0, 0, 210, 28, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('FractureDetect AI', 14, 14);
    doc.setFontSize(10);
    doc.text('Advanced Bone Fracture Detection System', 14, 20);

    doc.setFont('helvetica', 'normal');
    doc.setTextColor(255, 255, 255);
    doc.text(`Report ID: ${reportId}`, 150, 14);
    doc.text(`Date: ${genAt.toLocaleDateString()}`, 150, 20);

    doc.setDrawColor(230, 230, 230);
    doc.setLineWidth(0.4);
    doc.line(10, 30, 200, 30);

    // Patient Info in a light-grey table
    let y = 36;
    doc.setFillColor(245, 245, 245);
    doc.roundedRect(10, y, 190, 28, 2, 2, 'F');
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(60, 60, 60);
    doc.setFontSize(11);
    doc.text('Patient Information', 14, y + 6);

    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    const leftX = 14; const rightX = 110;
    let rowY = y + 12;
    doc.text('Name:', leftX, rowY); doc.text(user?.name || 'N/A', leftX + 22, rowY);
    doc.text('Age:', rightX, rowY); doc.text(user?.age ? String(user.age) : 'N/A', rightX + 18, rowY); rowY += 6;
    doc.text('Email:', leftX, rowY); doc.text(user?.email || 'N/A', leftX + 22, rowY);
    doc.text('Phone:', rightX, rowY); doc.text(user?.phone || 'N/A', rightX + 20, rowY); rowY += 6;
    doc.text('Region:', leftX, rowY); doc.text(result.body_region || 'N/A', leftX + 22, rowY);
    doc.text('Model Used:', rightX, rowY); doc.text(result.model_version || 'Unknown', rightX + 26, rowY);

    y = y + 32;

    // Detection Result hero section
    y = sectionBar('Detection Result', colors.results, y + 4);
    const statusColor = result.fracture_detected ? [220, 38, 38] : [34, 197, 94];
    const statusLabel = result.fracture_detected ? 'FRACTURE DETECTED' : 'NO FRACTURE DETECTED';
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(statusColor[0], statusColor[1], statusColor[2]);
    doc.setFontSize(20);
    doc.text(statusLabel, 105, y + 8, { align: 'center' });
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.text(`Confidence Score: ${(result.confidence * 100).toFixed(1)}%`, 105, y + 16, { align: 'center' });
    y += 24;

    const summaryText = result.fracture_detected
      ? 'AI suggests a possible bone fracture. Please consult an orthopedic specialist as soon as possible for a confirmatory clinical examination and treatment plan.'
      : 'AI did not detect a bone fracture in this X-ray. If pain, swelling, or difficulty moving continues, please consult a qualified doctor for further evaluation.';
    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    doc.text(summaryText, 14, y, { maxWidth: 182, lineHeightFactor: 1.4 });
    y += 16;
    doc.setTextColor(0, 0, 0);

    // X-ray image
    if (preview) {
      try {
        doc.setFontSize(12);
        doc.text('X-ray Analysis Image', 12, y);
        const imgY = y + 4;
        const imgW = 180; // keep aspect with height
        const imgH = 100;
        doc.addImage(preview, 'JPEG', 12, imgY, imgW, imgH);
        y = imgY + imgH + 4;
      } catch (e) {
        // ignore image add errors
      }
    }
    // Footer branding
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 1 | FractureDetect AI Report', 105, 290, { align: 'center' });

    // Page 2: Recommendations & Recovery
    doc.addPage();
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]); doc.rect(0, 0, 210, 10, 'F');
    y = sectionBar('Medical Recommendations', colors.recs, 14);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Dietary Guidelines', 12, y); y += 5;
    doc.setFont('helvetica', 'normal');
    const diet = [
      '• Increase Calcium: dairy, leafy greens, sardines',
      '• Vitamin D: fatty fish, fortified foods, sunlight',
      '• Protein: lean meats, beans, eggs, dairy',
      '• Vitamin C: citrus fruits, berries, bell peppers',
      '• Magnesium & Zinc: nuts, seeds, whole grains',
      '• Stay Hydrated: 8–10 glasses of water daily',
    ];
    diet.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.setFont('helvetica', 'bold'); doc.text('Medication / Treatment', 12, y); y += 5;
    doc.setFont('helvetica', 'normal');
    const tx = [
      '• Follow prescribed pain medications as directed',
      '• Consider anti-inflammatory drugs when recommended',
      '• Calcium and Vitamin D supplements as advised',
      '• Physical therapy as prescribed',
      '• Adequate rest and sleep for healing',
      '• Avoid smoking and limit alcohol',
    ];
    tx.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.setFont('helvetica', 'bold'); doc.text('Recovery Timeline', 12, y); y += 5;
    doc.setFont('helvetica', 'normal');
    const timeline = [
      '• 1–2 weeks: inflammation phase',
      '• 2–6 weeks: soft callus formation',
      '• 6–12 weeks: hard callus (bone strengthening)',
      '• 6–24 months: remodeling phase',
      '• Full recovery varies by fracture type and individual',
    ];
    timeline.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.setFont('helvetica', 'bold'); doc.text('Exercise Guidelines', 12, y); y += 5;
    doc.setFont('helvetica', 'normal');
    const ex = [
      '• Follow doctor-approved activity restrictions',
      '• Isometric exercises during immobilization',
      '• Gradual return to weight-bearing activities',
      '• Supervised physical therapy for mobility/strength',
      '• Avoid high-impact activities until cleared',
    ];
    ex.forEach(line => { doc.text(line, 16, y); y += 5; });
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 2 | FractureDetect AI Report', 105, 290, { align: 'center' });

    // Page 3: Nearby Hospitals + Disclaimer
    doc.addPage();
    doc.setFillColor(41, 128, 185); doc.rect(0, 0, 210, 10, 'F');
    doc.setTextColor(0,0,0); y = 18;
    y = sectionBar('Nearby Hospitals', colors.hospitals, 14);
    const hosps = nearbyHospitals && nearbyHospitals.length ? nearbyHospitals : [
      { name: 'City General Hospital', address: '123 Main Street, City Center', distance_km: 2.5, specialties: ['Orthopedics','Emergency Medicine'], website: 'https://city-general-hospital.example', rating: 4.4 },
      { name: 'Metropolitan Medical Center', address: '456 Oak Avenue, Downtown', distance_km: 4.2, specialties: ['Orthopedic Surgery','Sports Medicine'], website: 'https://metro-medical-center.example', rating: 4.3 },
      { name: 'University Orthopedic Clinic', address: '789 Pine Road, University District', distance_km: 6.8, specialties: ['Orthopedic Trauma','Hand Surgery'], website: 'https://university-ortho-clinic.example', rating: 4.5 },
      { name: 'Community Health Hospital', address: '321 Elm Street, Westside', distance_km: 7.3, specialties: ['General Medicine','Emergency Care'], website: 'https://community-health-hospital.example', rating: 4.1 },
      { name: 'Specialty Bone & Joint Center', address: '654 Cedar Boulevard, North District', distance_km: 9.1, specialties: ['Orthopedic Surgery','Spine Surgery'], website: 'https://bone-joint-center.example', rating: 4.6 },
    ];
    hosps.slice(0,5).forEach((h, idx) => {
      doc.setFillColor(248, 250, 252);
      doc.roundedRect(10, y, 190, 18, 2, 2, 'F');
      let innerY = y + 6;
      doc.setFontSize(12);
      doc.setTextColor(59,130,246);
      doc.text(`${idx+1}. ${h.name}`, 14, innerY); innerY += 4;
      doc.setFontSize(10);
      doc.setTextColor(0,0,0);
      doc.text(`Address: ${h.address}`, 14, innerY); innerY += 4;
      if (h.distance_km !== undefined) { doc.text(`Distance: ${h.distance_km} km`, 14, innerY); innerY += 4; }
      if (h.specialties) { doc.text(`Specialties: ${h.specialties.join(', ')}`, 14, innerY); innerY += 4; }
      if (h.website) { doc.text(`Website: ${h.website}`, 14, innerY); innerY += 4; }
      if (h.rating !== undefined && h.rating !== null) { doc.text(`Rating: ${h.rating} / 5`, 14, innerY); innerY += 4; }
      y = y + 20;
    });
    y += 6;
    y = sectionBar('Medical Disclaimer', colors.disclaimer, y);
    doc.setFontSize(10); doc.setTextColor(100,100,100);
    doc.text('This AI analysis is for informational purposes only. Always consult with a qualified healthcare professional.', 12, y, { maxWidth: 186, lineHeightFactor: 1.4 });
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 3 | FractureDetect AI Report', 105, 290, { align: 'center' });

    // Page 4: Model Evaluation Snapshots (curves + confusion + ROC)
    try {
      const metrics = await fetchMetricsImagesForPDF();
      if (metrics.curves || metrics.cm || metrics.roc) {
        doc.addPage();
        doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
        doc.rect(0, 0, 210, 10, 'F');
        let yEval = sectionBar('Model Evaluation Summary', colors.results, 14);
        doc.setFontSize(11);
        doc.text(`Model: ${result.model_version || metrics.slug}`, 12, yEval); yEval += 6;
        doc.text('These plots summarize how the model performed on its evaluation dataset.', 12, yEval, { maxWidth: 186 });
        yEval += 6;

        const imgW = 80;
        const imgH = 55;
        if (metrics.curves) {
          doc.addImage(metrics.curves, 'PNG', 16, yEval + 4, imgW, imgH);
          doc.setFontSize(9);
          doc.text('Figure 1: Training Accuracy & Loss', 16 + imgW / 2, yEval + imgH + 6, { align: 'center' });
        }
        if (metrics.cm) {
          doc.addImage(metrics.cm, 'PNG', 110, yEval + 4, imgW, imgH);
          doc.setFontSize(9);
          doc.text('Figure 2: Confusion Matrix', 110 + imgW / 2, yEval + imgH + 6, { align: 'center' });
        }
        yEval += imgH + 24;
        if (metrics.roc) {
          doc.addImage(metrics.roc, 'PNG', 16, yEval + 4, imgW, imgH);
          doc.setFontSize(9);
          doc.text('Figure 3: ROC Curve', 16 + imgW / 2, yEval + imgH + 6, { align: 'center' });
        }
        doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 4 | FractureDetect AI Report', 105, 290, { align: 'center' });
      }
    } catch (e) {
      // ignore metrics image errors
    }

    doc.save(`Fracture-Report-${genAt.toISOString().split('T')[0]}-${reportId}.pdf`);
  };

  const handleDownloadPDFTelugu = async () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const genAt = new Date();
    const reportId = `FD-TE-${genAt.getHours()}${genAt.getMinutes()}${genAt.getSeconds()}${genAt.getMilliseconds()}`;
    doc.setProperties({ title: 'FractureDetect AI Telugu Report' });

    const colors = {
      header: [34, 197, 94],
      patient: [34, 197, 94],
      results: [59, 130, 246],
      recs: [244, 114, 182],
      hospitals: [99, 102, 241],
      disclaimer: [100, 100, 100],
    };
    const sectionBar = (title, color, yPos) => {
      doc.setFillColor(color[0], color[1], color[2]);
      doc.rect(0, yPos, 210, 10, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(14);
      doc.text(title, 12, yPos + 7);
      doc.setTextColor(0, 0, 0);
      return yPos + 14;
    };

    // Page 1 Header
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
    doc.rect(0, 0, 210, 18, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(15);
    doc.text('FractureDetect AI', 12, 11);
    doc.setFontSize(11);
    doc.text('Fracture Report (Telugu-friendly style)', 12, 16);

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(9);
    doc.text(`Date: ${genAt.toLocaleDateString()}   Time: ${genAt.toLocaleTimeString()}   Report ID: ${reportId}`, 12, 24);

    // Page 1: Patient details + detection result + image
    let y = sectionBar('Rogi Vivaraalu (Patient Details)', colors.patient, 30);
    doc.setFillColor(245, 245, 245);
    doc.rect(10, y - 2, 190, 26, 'F');
    doc.setFontSize(11);
    doc.text(`Peru (Name): ${user?.name || 'Labhya kadu'}`, 14, y); y += 6;
    doc.text(`Email: ${user?.email || 'Labhya kadu'}`, 14, y); y += 6;
    if (user?.phone) { doc.text(`Phone: ${user.phone}`, 14, y); y += 6; }
    if (user?.age) { doc.text(`Vayassu (Age): ${user.age}`, 14, y); y += 4; }
    y += 6;

    // Detection results with highlight badge
    y = sectionBar('Pariksha Phalitallu (Results)', colors.results, y);
    const statusColorTe = result.fracture_detected ? [220, 38, 38] : [34, 197, 94];
    const statusLabelTe = result.fracture_detected
      ? 'Emuka virugu undi (Fracture undi)'
      : 'Emuka virugu ledu (Fracture ledu)';
    doc.setFillColor(statusColorTe[0], statusColorTe[1], statusColorTe[2]);
    doc.rect(12, y, 186, 10, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(13);
    doc.text(statusLabelTe, 105, y + 7, { align: 'center' });
    y += 16;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.text(`Nammaka shatam (Confidence): ${(result.confidence * 100).toFixed(1)}%`, 14, y); y += 6;
    doc.text(`Sharira bhagam (Region): ${result.body_region || 'Teliyadu'}`, 14, y); y += 6;
    doc.text(`Model peru: ${result.model_version || 'Teliyadu'}`, 14, y); y += 6;
    doc.text(`Model khachchitathvam: ${result.model_accuracy || 'Labhya kadu'}`, 14, y); y += 6;

    const summaryTe = result.fracture_detected
      ? 'AI pariksha prakaram emuka virugu undi ani suchistondi. Dhayachesi orthopaedic doctor ni tvaraga kalisi, sariyaina chikitsa teesukondi.'
      : 'AI pariksha prakaram emuka virugu ledu ani chupisthondi. Kani noppulu, vapu, ledha chalana kastam unte doctor ni tappakunda kalavandi.';
    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    doc.text(summaryTe, 14, y, { maxWidth: 182 });
    y += 16;
    doc.setTextColor(0, 0, 0);

    // X-ray image section
    if (preview) {
      try {
        doc.setFontSize(12);
        doc.text('X-ray Chitram (AI Vishleshana)', 12, y);
        const imgY = y + 4;
        const imgW = 180;
        const imgH = 100;
        doc.addImage(preview, 'JPEG', 12, imgY, imgW, imgH);
        y = imgY + imgH + 4;
      } catch (e) {
        // ignore image add errors
      }
    }
    doc.setFontSize(9);
    doc.setTextColor(120, 120, 120);
    doc.text('Page 1 of 3 (Telugu)', 105, 290, { align: 'center' });

    // Page 2: Diet, treatment & recovery suggestions
    doc.addPage();
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
    doc.rect(0, 0, 210, 10, 'F');
    y = sectionBar('Aaharam & Chikitsa Suchanalu', colors.recs, 14);
    doc.setFontSize(12);
    doc.text('Aaharam (Diet) Suchanalu:', 12, y); y += 5;
    const dietTe = [
      '• Calcium ekkuva unna aaharam: paalu, perugu, leafy greens',
      '• Vitamin D kosam: sun light, fish, fortified foods',
      '• Protein: pappulu, eggs, lean meats, milk products',
      '• Vitamin C: oranges, mosambi, berries, bell pepper',
      '• Nuts, seeds, whole grains dwara minerals pondandi',
    ];
    dietTe.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;

    doc.setFontSize(12);
    doc.text('Chikitsa (Treatment) Suchanalu:', 12, y); y += 5;
    const treatTe = [
      '• Doctor ichina pain tablets ni tappakunda follow avvandi',
      '• Ice pack 10–15 nimishalu veyandi, direct skin avoid cheyandi',
      '• Gayam unna cheyi / kalu ni etthuga petti rest ivvandi',
      '• Physical therapy doctor cheppinattu matrame cheyandi',
      '• Smoking maninchandi, alcohol tagginchandi',
    ];
    treatTe.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;

    doc.setFontSize(12);
    doc.text('Recovery Samayam (Timeline):', 12, y); y += 5;
    const timeTe = [
      '• 1–2 varalu: inflammation phase (prarambha vapu & noppulu)',
      '• 2–6 varalu: soft callus (mellaga guddu cheradam prarambham)',
      '• 6–12 varalu: hard callus (emuka balam perigina dasa)',
      '• 6–24 nelalu: remodeling (emuka full strong avvadam)',
    ];
    timeTe.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;

    doc.setFontSize(12);
    doc.text('Vyayaama Suchanalu (Exercise):', 12, y); y += 5;
    const exTe = [
      '• Doctor cheppina varaku heavy pani, running, jumping avoid cheyandi',
      '• Immobilization time lo simple isometric exercises cheyavachu',
      '• Malla weight-bearing start cheyyali ante doctor guidance lo matrame',
      '• Physiotherapy unte, appointments ni miss kakunda vellandi',
    ];
    exTe.forEach(line => { doc.text(line, 16, y); y += 5; });

    doc.setFontSize(9);
    doc.setTextColor(120, 120, 120);
    doc.text('Page 2 of 3 (Telugu)', 105, 290, { align: 'center' });

    // Page 3: Nearby hospitals & disclaimer (Telugu-friendly)
    doc.addPage();
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
    doc.rect(0, 0, 210, 10, 'F');
    doc.setTextColor(0, 0, 0);
    y = sectionBar('Daggarlo unna Aaspatalu (Nearby Hospitals)', colors.hospitals, 14);

    const hosps = nearbyHospitals && nearbyHospitals.length ? nearbyHospitals : [
      { name: 'City General Hospital', address: '123 Main Street, City Center', distance_km: 2.5, specialties: ['Orthopedics','Emergency Medicine'], website: 'https://city-general-hospital.example', rating: 4.4 },
      { name: 'Metropolitan Medical Center', address: '456 Oak Avenue, Downtown', distance_km: 4.2, specialties: ['Orthopedic Surgery','Sports Medicine'], website: 'https://metro-medical-center.example', rating: 4.3 },
      { name: 'University Orthopedic Clinic', address: '789 Pine Road, University District', distance_km: 6.8, specialties: ['Orthopedic Trauma','Hand Surgery'], website: 'https://university-ortho-clinic.example', rating: 4.5 },
      { name: 'Community Health Hospital', address: '321 Elm Street, Westside', distance_km: 7.3, specialties: ['General Medicine','Emergency Care'], website: 'https://community-health-hospital.example', rating: 4.1 },
      { name: 'Specialty Bone & Joint Center', address: '654 Cedar Boulevard, North District', distance_km: 9.1, specialties: ['Orthopedic Surgery','Spine Surgery'], website: 'https://bone-joint-center.example', rating: 4.6 },
    ];
    hosps.slice(0, 5).forEach((h, idx) => {
      doc.setFontSize(12);
      doc.setTextColor(59, 130, 246);
      doc.text(`${idx + 1}. ${h.name}`, 12, y); y += 5;
      doc.setFontSize(10);
      doc.setTextColor(0, 0, 0);
      doc.text(`Address: ${h.address}`, 16, y); y += 4;
      if (h.distance_km !== undefined) { doc.text(`Distance: ${h.distance_km} km`, 16, y); y += 4; }
      if (h.specialties) { doc.text(`Specialties: ${h.specialties.join(', ')}`, 16, y); y += 4; }
      if (h.website) { doc.text(`Website: ${h.website}`, 16, y); y += 4; }
      if (h.rating !== undefined && h.rating !== null) { doc.text(`Rating: ${h.rating} / 5`, 16, y); y += 4; }
      y += 2;
    });

    y += 6;
    y = sectionBar('Suchana Matrame (Disclaimer)', colors.disclaimer, y);
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(
      'Ee AI report samachara kosam matrame. Nijamaina diagnosis mariyu treatment kosam tappakunda MBBS / specialist doctor ni kalasi vaari margadarshanam follow avvandi.',
      12,
      y,
      { maxWidth: 186 }
    );

    doc.setFontSize(9);
    doc.setTextColor(120, 120, 120);
    doc.text('Page 3 of 3 (Telugu)', 105, 290, { align: 'center' });

    // Page 4: Model Evaluation (Telugu-friendly captions)
    try {
      const metrics = await fetchMetricsImagesForPDF();
      if (metrics.curves || metrics.cm || metrics.roc) {
        doc.addPage();
        doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
        doc.rect(0, 0, 210, 10, 'F');
        let yEval = sectionBar('Model Parishkara Phalitallu', colors.results, 14);
        doc.setFontSize(11);
        doc.text(`Model: ${result.model_version || metrics.slug}`, 12, yEval); yEval += 6;
        doc.text('Ee chitrala dwara model ela nerchukundho mariyu ela perform chesindho chupisthayi.', 12, yEval, { maxWidth: 186 });
        yEval += 6;

        const imgW = 80;
        const imgH = 55;
        if (metrics.curves) {
          doc.text('Accuracy & Loss Curves', 16, yEval + 4);
          doc.addImage(metrics.curves, 'PNG', 16, yEval + 6, imgW, imgH);
        }
        if (metrics.cm) {
          doc.text('Confusion Matrix', 110, yEval + 4);
          doc.addImage(metrics.cm, 'PNG', 110, yEval + 6, imgW, imgH);
        }
        yEval += imgH + 20;
        if (metrics.roc) {
          doc.text('ROC Curve', 16, yEval + 4);
          doc.addImage(metrics.roc, 'PNG', 16, yEval + 6, imgW, imgH);
        }

        doc.setFontSize(9);
        doc.setTextColor(120, 120, 120);
        doc.text('Page 4 of 4 (Telugu)', 105, 290, { align: 'center' });
      }
    } catch (e) {
      // ignore metrics image errors
    }

    doc.save(`Fracture-Report-TE-${genAt.toISOString().split('T')[0]}-${reportId}.pdf`);
  };

  const handleDownloadReport = async () => {
    if (!result) return;
    const choice = window.prompt('Choose report language: type EN for English or TE for Telugu', 'EN');
    if (!choice) return;
    const val = choice.trim().toLowerCase();
    if (val === 'te' || val === 'telugu') {
      await handleDownloadPDFTelugu();
    } else {
      await handleDownloadPDF();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('Prediction result:', response.data);
      setResult(response.data);
    } catch (err) {
      console.error('Error uploading file:', err);
      if (err.response) {
        if (err.response.status === 401) {
          alert('Session expired. Please log in again.');
          handleLogout();
        } else {
          setError(`Error: ${err.response.data.error || 'Could not process the image.'}`);
        }
      } else {
        setError('Network error. Please ensure the backend is running and accessible.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    setChatHistory(prev => [...prev, userMsg]);
    setChatInput('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/chat', {
        message: userMsg.content,
        context: result
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setChatHistory(prev => [...prev, { role: 'ai', content: response.data.response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: "Sorry, I couldn't get a response." }]);
    }
  };

  const requestLocationAccess = async () => {
    if (!navigator.geolocation) {
      setShowLocationPermissionModal(false);
      setNearbyHospitals([]);
      setShowHospitalsModal(true);
      return;
    }
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const { latitude, longitude } = pos.coords;
        // Open real Google Maps search at the user's GPS location for accurate nearby hospitals
        const mapsUrl = `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},15z`;
        window.open(mapsUrl, '_blank', 'noopener,noreferrer');

        // Also call backend to keep the in-app list populated as a fallback
        try {
          const resp = await axios.post('http://localhost:5000/nearby_hospitals', { latitude, longitude });
          if (resp.data && resp.data.hospitals) {
            setNearbyHospitals(resp.data.hospitals);
          }
        } catch (innerErr) {
          console.error('Error getting hospitals from backend:', innerErr);
          setNearbyHospitals([]);
        }
      } catch (e) {
        console.error('Error getting hospitals:', e);
        setNearbyHospitals([]);
      } finally {
        setShowLocationPermissionModal(false);
        setShowHospitalsModal(true);
      }
    }, (err) => {
      console.error('Geolocation error:', err);
      setNearbyHospitals([]);
      setShowLocationPermissionModal(false);
      setShowHospitalsModal(true);
    });
  };

  const handleFindHospitals = () => {
    setShowLocationPermissionModal(true);
  };

  const renderView = () => {
    console.log('Rendering view:', currentView);
    switch (currentView) {
      case 'login':
        return <Login onLoginSuccess={handleLoginSuccess} />;
      case 'signup':
        return <Signup onSignupSuccess={() => setCurrentView('login')} onLoginSuccess={handleLoginSuccess} />;
      case 'history':
        return <History user={user} onBack={() => setCurrentView('app')} />;
      case 'analytics':
        return renderAnalytics();
      default:
        return renderApp();
    }
  };

  const fetchAnalytics = async () => {
    try {
      setLoadingAnalytics(true);
      setAnalyticsError('');
      const token = localStorage.getItem('token');
      const resp = await axios.get('http://localhost:5000/admin/analytics', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setAnalytics(resp.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setAnalyticsError('Could not load analytics. Please ensure backend and database are running.');
    } finally {
      setLoadingAnalytics(false);
    }
  };

  const renderAnalytics = () => {
    if (!user) {
      return (
        <div className="app-container">
          <header className="header">
            <div className="logo"><FiFileText /> FractureDetect AI</div>
          </header>
          <main className="main-content">
            <p>Please log in to view analytics.</p>
          </main>
        </div>
      );
    }

    if (!analytics && !loadingAnalytics && !analyticsError) {
      // First time entering analytics view
      fetchAnalytics();
    }

    const total = analytics?.total_scans || 0;
    const fractureRate = analytics ? (analytics.fracture_rate * 100).toFixed(1) : '0.0';
    const avgConf = analytics ? (analytics.average_confidence * 100).toFixed(1) : '0.0';

    const maxDayCount = analytics?.scans_per_day?.reduce((m, d) => Math.max(m, d.count), 0) || 1;
    const maxRegionCount = analytics?.body_region_distribution?.reduce((m, r) => Math.max(m, r.count), 0) || 1;

    return (
      <div className="app-container">
        <header className="header">
          <div className="logo"><FiFileText /> FractureDetect AI</div>
          <div className="user-info">
            <div className="user-welcome">
              <FiUser />
              <span>Dashboard</span>
            </div>
            <nav className="navigation">
              <button className="nav-btn" onClick={() => setCurrentView('app')}>
                Back to App
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                <FiLogOut /> Logout
              </button>
            </nav>
          </div>
        </header>

        <main className="main-content analytics-main">
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-subtitle">AI usage analytics over the last 30 days.</p>

          {loadingAnalytics && <p>Loading analytics…</p>}
          {analyticsError && <div className="error-message"><FiAlertTriangle /> {analyticsError}</div>}

          {analytics && !loadingAnalytics && !analyticsError && (
            <>
              <div className="analytics-summary-grid">
                <div className="analytics-card">
                  <div className="analytics-label">Total Scans</div>
                  <div className="analytics-value">{total}</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-label">% Fracture Detected</div>
                  <div className="analytics-value">{fractureRate}%</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-label">Avg. Model Confidence</div>
                  <div className="analytics-value">{avgConf}%</div>
                </div>
              </div>

              <div className="analytics-charts-grid">
                <div className="analytics-chart-card">
                  <h3>Scans Per Day</h3>
                  {analytics.scans_per_day && analytics.scans_per_day.length > 0 ? (
                    <div className="bar-chart">
                      {analytics.scans_per_day.map((d) => (
                        <div key={d.date} className="bar-item">
                          <div
                            className="bar-fill"
                            style={{ height: `${(d.count / maxDayCount) * 100}%` }}
                            title={`${d.date}: ${d.count} scans`}
                          />
                          <div className="bar-label">{d.date.slice(5)}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No scans recorded yet.</p>
                  )}
                </div>

                <div className="analytics-chart-card">
                  <h3>Most Common Body Regions</h3>
                  {analytics.body_region_distribution && analytics.body_region_distribution.length > 0 ? (
                    <div className="bar-chart horizontal">
                      {analytics.body_region_distribution.map((r) => (
                        <div key={r.region} className="bar-item-horizontal">
                          <div className="bar-label-horizontal">{r.region}</div>
                          <div className="bar-track-horizontal">
                            <div
                              className="bar-fill-horizontal"
                              style={{ width: `${(r.count / maxRegionCount) * 100}%` }}
                              title={`${r.region}: ${r.count} scans`}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No region data yet.</p>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    );
  };

  const renderApp = () => {
    console.log('Rendering App, user:', user, 'result:', result);
    return (
    <div className="app-container">
      <header className="header">
        <div className="logo">
          <FiFileText /> FractureDetect AI
        </div>
        {user && (
          <div className="user-info">
            <div className="user-welcome">
              <FiUser />
              <span>Welcome, {user.name}</span>
              <div className="user-status">
                <div className="status-indicator"></div>
                <span>Online</span>
              </div>
            </div>
            <nav className="navigation">
              <button className="nav-btn" onClick={() => window.location.hash = 'history'}>
                <FiFileText /> History
              </button>
              <button className="nav-btn" onClick={() => { setCurrentView('analytics'); }}>
                Analytics
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                <FiLogOut /> Logout
              </button>
            </nav>
          </div>
        )}
      </header>

      <main className="main-content">
        {!result ? (
          <div className="upload-section">
            <h1 className="hero-title">Upload Your X-Ray Image</h1>
            <p className="hero-subtitle">Get an instant AI-powered fracture analysis.</p>
            <div className="upload-card">
              <form onSubmit={handleSubmit}>
                <label 
                  htmlFor="file-upload" 
                  className={`upload-label ${preview ? 'has-preview' : ''} ${isDragging ? 'dragging' : ''}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  {preview ? (
                    <img src={preview} alt="X-ray preview" className="image-preview" />
                  ) : (
                    <div className="upload-placeholder">
                      <FiUploadCloud />
                      <span>{file ? file.name : "Click or drag to upload"}</span>
                      <p>Supports JPEG, PNG, BMP, TIFF formats</p>
                    </div>
                  )}
                </label>
                <input
                  id="file-upload"
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="file-input"
                />
                <button type="submit" className="analyze-btn" disabled={!file || loading}>
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      Analyzing...
                    </>
                  ) : 'Analyze Image'}
                </button>
              </form>
              {error && <div className="error-message"><FiAlertTriangle /> {error}</div>}
            </div>
          </div>
        ) : (
          <div className="results-section">
            <h1 className="hero-title">Analysis Complete</h1>
            <div className="results-grid">
              <div className="result-card">
                <h3>Detection Result</h3>
                <div className={`status ${result.fracture_detected ? 'fracture' : 'normal'}`}>
                  {result.fracture_detected ? <FiAlertTriangle /> : <FiCheckCircle />}
                  <span>{result.fracture_detected ? 'Fracture Detected' : 'No Fracture Detected'}</span>
                </div>
                <div className="result-details">
                  <div className="detail-item">
                    <FiActivity />
                    <div>
                      <span className="detail-label">Confidence</span>
                      <span className="detail-value">{(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiFileText />
                    <div>
                      <span className="detail-label">Model Used</span>
                      <span className="detail-value model-name-display">{result.model_version}</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiCheckCircle />
                    <div>
                      <span className="detail-label">Model Accuracy</span>
                      <span className="detail-value">{result.model_accuracy}</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiClock />
                    <div>
                      <span className="detail-label">Analysis Time</span>
                      <span className="detail-value">{new Date().toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
                <div className="result-actions">
                  <button onClick={handleDownloadReport}><FiDownload /> Download Report</button>
                  <button onClick={() => speakResult('en')}><FiVolume2 /> Voice (EN)</button>
                  <button onClick={() => speakResult('te')}><FiVolume2 /> Voice (TE)</button>
                  <button onClick={() => setShowChat(true)}><FiMessageSquare /> Medical Assistant</button>
                  <button onClick={handleFindHospitals}><FiMapPin /> Find Hospitals</button>
                </div>
              </div>
              <div className="image-card">
                <h3>Analysis Result</h3>
                <img 
                  src={result.annotated_image || preview} 
                  alt={result.annotated_image ? "Annotated X-ray with detection results" : "X-ray"} 
                />
                {result.annotated_image && (
                  <p style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--text-lighter)' }}>
                    Image shows detection overlays and confidence metrics
                  </p>
                )}
                <button
                  className="outputs-btn"
                  type="button"
                  onClick={() => setShowOutputs(prev => !prev)}
                >
                  {showOutputs ? 'Hide Outputs' : 'Outputs'}
                </button>
              </div>
            </div>
            {showOutputs && (
              <div className="outputs-panel">
                <h2>Model Evaluation Outputs</h2>
                <div className="outputs-model-grid">
                  {['EfficientNet', 'DenseNet121', 'DenseNet169', 'ResNet50'].map((name) => {
                    const slugMap = {
                      EfficientNet: 'efficientnet',
                      DenseNet121: 'densenet121',
                      DenseNet169: 'densenet169',
                      ResNet50: 'resnet50',
                    };
                    const slug = slugMap[name] || name.toLowerCase();
                    const baseUrl = 'http://localhost:5000/metrics';
                    const imgBase = `${baseUrl}/${slug}`;
                    return (
                      <div key={name} className="model-output-card">
                        <h3>{name}</h3>
                        <div className="metric-row">
                          <div className="metric-item">
                            <div className="metric-title">Accuracy & Loss</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_training_curves.png`}
                              alt={`${name} training/validation accuracy & loss curves`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                          <div className="metric-item">
                            <div className="metric-title">Confusion Matrix</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_confusion_matrix.png`}
                              alt={`${name} confusion matrix`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                        </div>
                        <div className="metric-row">
                          <div className="metric-item">
                            <div className="metric-title">Metrics Table</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_metrics_table.png`}
                              alt={`${name} classification metrics table`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                          <div className="metric-item">
                            <div className="metric-title">ROC Curve</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_roc_curve.png`}
                              alt={`${name} ROC curve`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                        </div>
                        <div className="metric-row">
                          <div className="metric-item">
                            <div className="metric-title">Model Comparison</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_comparison.png`}
                              alt={`${name} comparison within ensemble`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                          <div className="metric-item">
                            <div className="metric-title">Sample Outputs</div>
                            <img
                              className="metric-image"
                              src={`${imgBase}_sample_outputs.png`}
                              alt={`${name} sample prediction outputs`}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}

                  <div className="model-output-card">
                    <h3>FracNet (U-Net Segmentation)</h3>
                    <div className="metric-row">
                      <div className="metric-item">
                        <div className="metric-title">Accuracy & Loss</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_training_curves.png`}
                          alt="FracNet segmentation training/validation curves"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                      <div className="metric-item">
                        <div className="metric-title">Confusion Matrix</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_confusion_matrix.png`}
                          alt="FracNet confusion matrix"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    </div>
                    <div className="metric-row">
                      <div className="metric-item">
                        <div className="metric-title">Dice / IoU</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_segmentation_metrics.png`}
                          alt="FracNet Dice / IoU metrics"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                      <div className="metric-item">
                        <div className="metric-title">ROC / PR Curves</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_roc_pr_curves.png`}
                          alt="FracNet ROC / PR curves"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    </div>
                    <div className="metric-row">
                      <div className="metric-item">
                        <div className="metric-title">Segmentation Outputs</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_segmentation_examples.png`}
                          alt="FracNet segmentation output examples"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                      <div className="metric-item">
                        <div className="metric-title">Sample Outputs</div>
                        <img
                          className="metric-image"
                          src={`http://localhost:5000/metrics/fracnet_sample_outputs.png`}
                          alt="FracNet sample prediction outputs"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <button className="upload-another-btn" onClick={handleUploadAnother}><FiPlus /> Upload Another</button>
          </div>
        )}
      </main>

      {showChat && (
        <div className="chat-overlay">
          <div className="chat-window">
            <div className="chat-header">
              <h3>Medical Assistant</h3>
              <button onClick={() => setShowChat(false)}><FiX /></button>
            </div>
            <div className="chat-messages" ref={chatMessagesRef}>
              <div className="chat-intro">
                <FiHeart />
                <p>Hello! I'm your AI medical assistant. How can I help you with your fracture analysis?</p>
              </div>
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  {msg.content}
                </div>
              ))}
            </div>
            <form className="chat-input-form" onSubmit={handleChatSubmit}>
              <input
                type="text"
                placeholder="Ask a question..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit"><FiSend /></button>
            </form>
          </div>
        </div>
      )}

      {showLocationPermissionModal && (
        <div className="location-overlay" onClick={() => setShowLocationPermissionModal(false)}>
          <div className="location-window" onClick={(e) => e.stopPropagation()}>
            <div className="location-header">
              <h3><FiMapPin /> Location Permission</h3>
              <button className="close-btn" onClick={() => setShowLocationPermissionModal(false)}><FiX /></button>
            </div>
            <div className="location-body">
              <p>We use your location to list nearby hospitals for faster clinical access. Please allow location access.</p>
              <div className="location-actions">
                <button className="nav-btn" onClick={requestLocationAccess}><FiMapPin /> Allow Location Access</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showHospitalsModal && (
        <div className="hospitals-overlay" onClick={() => setShowHospitalsModal(false)}>
          <div className="hospitals-window" onClick={(e) => e.stopPropagation()}>
            <div className="hospitals-header">
              <h3><FiMapPin /> Nearby Hospitals</h3>
              <button className="close-btn" onClick={() => setShowHospitalsModal(false)}><FiX /></button>
            </div>
            <div className="hospitals-list">
              {(nearbyHospitals && nearbyHospitals.length ? nearbyHospitals : [
                { name: 'City General Hospital', address: '123 Main Street, City Center', distance_km: 2.5, specialties: ['Orthopedics','Emergency Medicine'], website: 'https://city-general-hospital.example', rating: 4.4 },
                { name: 'Metropolitan Medical Center', address: '456 Oak Avenue, Downtown', distance_km: 4.2, specialties: ['Orthopedic Surgery','Sports Medicine'], website: 'https://metro-medical-center.example', rating: 4.3 },
                { name: 'University Orthopedic Clinic', address: '789 Pine Road, University District', distance_km: 6.8, specialties: ['Orthopedic Trauma','Hand Surgery'], website: 'https://university-ortho-clinic.example', rating: 4.5 },
                { name: 'Community Health Hospital', address: '321 Elm Street, Westside', distance_km: 7.3, specialties: ['General Medicine','Emergency Care'], website: 'https://community-health-hospital.example', rating: 4.1 },
                { name: 'Specialty Bone & Joint Center', address: '654 Cedar Boulevard, North District', distance_km: 9.1, specialties: ['Orthopedic Surgery','Spine Surgery'], website: 'https://bone-joint-center.example', rating: 4.6 },
              ]).slice(0,5).map((h, idx) => (
                <div className="hospital-item" key={idx}>
                  <div className="hospital-icon"><FiSearch /></div>
                  <div className="hospital-info">
                    <div className="hospital-name">{h.name}</div>
                    <div className="hospital-meta">{h.address}</div>
                    {h.distance_km !== undefined && (
                      <div className="hospital-meta">Distance: {h.distance_km} km</div>
                    )}
                    {h.specialties && (
                      <div className="hospital-meta">Specialties: {h.specialties.join(', ')}</div>
                    )}
                    {h.website && (
                      <div className="hospital-meta">Website: {h.website}</div>
                    )}
                    {h.rating !== undefined && h.rating !== null && (
                      <div className="hospital-meta">Rating: {h.rating} / 5</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
  };

  return renderView();
}

export default App;
