'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  requestMicrophonePermission,
  requestCameraPermission,
  checkPermissionStatus,
  createAudioAnalyser,
  stopStream,
} from '@/lib/mediaDevices';

/**
 * useMediaDevices
 * Custom hook to manage microphone and camera lifecycle, including
 * permission checking, stream requesting, and real-time audio level monitoring.
 */
export function useMediaDevices() {
  const [micStatus, setMicStatus] = useState('prompt'); // 'prompt' | 'granted' | 'denied'
  const [camStatus, setCamStatus] = useState('prompt'); // 'prompt' | 'granted' | 'denied'
  
  const [micStream, setMicStream] = useState(null);
  const [camStream, setCamStream] = useState(null);
  
  const [audioLevel, setAudioLevel] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isCameraOff, setIsCameraOff] = useState(false);

  const analyserRef = useRef(null);
  const rafRef = useRef(null);
  const micStreamRef = useRef(null);
  const camStreamRef = useRef(null);

  // Check initial permission status on mount
  useEffect(() => {
    let active = true;
    Promise.all([
      checkPermissionStatus('microphone'),
      checkPermissionStatus('camera')
    ]).then(([mic, cam]) => {
      if (!active) return;
      setMicStatus(mic);
      setCamStatus(cam);
    });
    return () => { active = false; };
  }, []);

  // Update audio level continuously if mic is active and not muted
  useEffect(() => {
    if (!micStream || isMuted) {
      setAudioLevel(0);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }

    if (!analyserRef.current) {
      analyserRef.current = createAudioAnalyser(micStream);
    }

    const updateLevel = () => {
      if (analyserRef.current) {
        setAudioLevel(analyserRef.current.getLevel());
      }
      rafRef.current = requestAnimationFrame(updateLevel);
    };

    updateLevel();

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [micStream, isMuted]);

  const requestMic = useCallback(async () => {
    const result = await requestMicrophonePermission();
    if (result.granted && result.stream) {
      micStreamRef.current = result.stream;
      setMicStream(result.stream);
      setMicStatus('granted');
    } else {
      setMicStatus('denied');
    }
    return result;
  }, []);

  const requestCam = useCallback(async () => {
    const result = await requestCameraPermission();
    if (result.granted && result.stream) {
      camStreamRef.current = result.stream;
      setCamStream(result.stream);
      setCamStatus('granted');
    } else {
      setCamStatus('denied');
    }
    return result;
  }, []);

  const toggleMute = useCallback(() => {
    if (micStream) {
      const audioTracks = micStream.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!audioTracks.every(t => t.enabled));
    }
  }, [micStream]);

  const toggleCamera = useCallback(() => {
    if (camStream) {
      const videoTracks = camStream.getVideoTracks();
      videoTracks.forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsCameraOff(!videoTracks.every(t => t.enabled));
    }
  }, [camStream]);

  const stopAll = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (analyserRef.current) {
      analyserRef.current.cleanup();
      analyserRef.current = null;
    }
    stopStream(micStreamRef.current);
    stopStream(camStreamRef.current);
    micStreamRef.current = null;
    camStreamRef.current = null;
    setMicStream(null);
    setCamStream(null);
    setAudioLevel(0);
    setIsMuted(false);
    setIsCameraOff(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopAll();
  }, [stopAll]);

  return {
    micStatus,
    camStatus,
    micStream,
    camStream,
    audioLevel,
    isMuted,
    isCameraOff,
    requestMic,
    requestCam,
    toggleMute,
    toggleCamera,
    stopAll
  };
}
