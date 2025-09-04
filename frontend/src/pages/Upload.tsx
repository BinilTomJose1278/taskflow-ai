import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  TextField,
  Alert,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as DocumentIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { documentApi } from '../services/api';

interface UploadedFile {
  file: File;
  title: string;
  description: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  response?: any;
  error?: string;
}

const Upload: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    const uploadFiles: UploadedFile[] = newFiles.map(file => ({
      file,
      title: file.name.split('.')[0],
      description: '',
      status: 'pending',
    }));
    setFiles(prev => [...prev, ...uploadFiles]);
  };

  const updateFile = (index: number, updates: Partial<UploadedFile>) => {
    setFiles(prev => prev.map((file, i) => 
      i === index ? { ...file, ...updates } : file
    ));
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (index: number) => {
    const fileData = files[index];
    updateFile(index, { status: 'uploading' });

    try {
      const response = await documentApi.uploadDocument(
        fileData.file,
        fileData.title,
        fileData.description
      );
      updateFile(index, { status: 'success', response });
    } catch (error) {
      updateFile(index, { 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Upload failed' 
      });
    }
  };

  const uploadAllFiles = async () => {
    for (let i = 0; i < files.length; i++) {
      if (files[i].status === 'pending') {
        await uploadFile(i);
      }
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'uploading':
        return <LinearProgress sx={{ width: 20, height: 20 }} />;
      default:
        return <DocumentIcon color="action" />;
    }
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          📤 Upload Documents
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Upload documents for AI-powered processing and analysis
        </Typography>
      </Box>

      {/* Upload Area */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Paper
            variant="outlined"
            sx={{
              p: 4,
              textAlign: 'center',
              border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
              backgroundColor: dragActive ? '#f5f5f5' : 'transparent',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <UploadIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {dragActive ? 'Drop files here' : 'Drag & drop files here'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              or click to browse files
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Supports PDF, DOC, DOCX, TXT, and image files
            </Typography>
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />
          </Paper>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="div">
                Files to Upload ({files.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<UploadIcon />}
                onClick={uploadAllFiles}
                disabled={files.every(f => f.status !== 'pending')}
              >
                Upload All
              </Button>
            </Box>

            <List>
              {files.map((fileData, index) => (
                <ListItem key={index} divider>
                  <ListItemIcon>
                    {getStatusIcon(fileData.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {fileData.file.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ({(fileData.file.size / 1024 / 1024).toFixed(2)} MB)
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <TextField
                          fullWidth
                          size="small"
                          label="Title"
                          value={fileData.title}
                          onChange={(e) => updateFile(index, { title: e.target.value })}
                          sx={{ mb: 1 }}
                        />
                        <TextField
                          fullWidth
                          size="small"
                          label="Description (optional)"
                          value={fileData.description}
                          onChange={(e) => updateFile(index, { description: e.target.value })}
                          multiline
                          rows={2}
                        />
                        {fileData.status === 'error' && (
                          <Alert severity="error" sx={{ mt: 1 }}>
                            {fileData.error}
                          </Alert>
                        )}
                        {fileData.status === 'success' && (
                          <Alert severity="success" sx={{ mt: 1 }}>
                            Upload successful! File: {fileData.response?.filename}
                          </Alert>
                        )}
                      </Box>
                    }
                  />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {fileData.status === 'pending' && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => uploadFile(index)}
                      >
                        Upload
                      </Button>
                    )}
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => removeFile(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default Upload;
