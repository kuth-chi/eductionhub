# Education Form - Attachment Upload UI

## Visual Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ Education Form                                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ Degree / Qualification *                                         │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Bachelor of Science in Computer Science                    │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ Institution (Optional)                                           │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Search for a school...                              [×]    │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ Start Date *              End Date *                             │
│ ┌────────────────────┐   ┌────────────────────┐                 │
│ │ 2020-01-01        │   │ 2024-06-30        │                 │
│ └────────────────────┘   └────────────────────┘                 │
│                                                                   │
│ Description *                                                     │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Completed comprehensive program in Computer Science...     │  │
│ │                                                             │  │
│ │                                                             │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Attachments (Optional)                      [📤 Add Files]      │
│ Upload certificates, transcripts, or other documents             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ 📄 degree-certificate.pdf (124.5 KB)              [×]   │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ 📄 transcript.pdf (89.2 KB)                       [×]   │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│ Current Attachments:                                             │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ 📄 previous-certificate.pdf                            │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                              [Cancel]  [Save]    │
└──────────────────────────────────────────────────────────────────┘
```

## Component States

### 1. Default State (No Files)
```
┌──────────────────────────────────────────────────────────────┐
│ Attachments (Optional)                  [📤 Add Files]      │
│ Upload certificates, transcripts, or other documents         │
└──────────────────────────────────────────────────────────────┘
```

### 2. Uploading State
```
┌──────────────────────────────────────────────────────────────┐
│ Attachments (Optional)                  [📤 Uploading...]   │
│ Upload certificates, transcripts, or other documents         │
└──────────────────────────────────────────────────────────────┘
```

### 3. With Files Selected
```
┌──────────────────────────────────────────────────────────────┐
│ Attachments (Optional)                  [📤 Add Files]      │
│ Upload certificates, transcripts, or other documents         │
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 📄 certificate.pdf (124.5 KB)                  [×]    │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 📄 transcript.pdf (89.2 KB)                    [×]    │  │
│ └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 4. Error State
```
┌──────────────────────────────────────────────────────────────┐
│ Attachments (Optional)                  [📤 Add Files]      │
│ Upload certificates, transcripts, or other documents         │
├──────────────────────────────────────────────────────────────┤
│ ⚠️ Failed to upload files. Please try again.                 │
└──────────────────────────────────────────────────────────────┘
```

### 5. Edit Mode with Existing Attachments
```
┌──────────────────────────────────────────────────────────────┐
│ Attachments (Optional)                  [📤 Add Files]      │
│ Upload certificates, transcripts, or other documents         │
├──────────────────────────────────────────────────────────────┤
│ Current Attachments:                                          │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 📄 previous-certificate.pdf                          │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 📄 old-transcript.pdf                                │  │
│ └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## File Card Design

### Normal File Card
```
┌─────────────────────────────────────────────────────────┐
│ 📄 degree-certificate.pdf (124.5 KB)          [×]      │
└─────────────────────────────────────────────────────────┘
```

**Breakdown:**
- Icon: 📄 (FileText icon from lucide-react)
- File Name: `degree-certificate.pdf`
- File Size: `(124.5 KB)`
- Remove Button: `[×]` (X icon, ghost variant)

**Styling:**
- Border: `rounded-md border`
- Background: `bg-muted/50`
- Padding: `p-3`
- Layout: `flex items-center justify-between`

### Existing Attachment Card
```
┌─────────────────────────────────────────────────────────┐
│ 📄 previous-certificate.pdf                            │
└─────────────────────────────────────────────────────────┘
```

**Breakdown:**
- Icon: 📄 (FileText icon)
- File Name: `previous-certificate.pdf` (clickable link)
- No remove button (existing files)

**Styling:**
- Border: `rounded-md border`
- Background: `bg-muted/30`
- Padding: `p-2`
- Layout: `flex items-center gap-2`

## Button States

### Add Files Button
```
Normal:     [📤 Add Files]
Uploading:  [📤 Uploading...] (disabled)
```

### Remove Button
```
Normal:     [×]
Hover:      [×] (ghost hover effect)
```

## Accepted File Types

Visual indicator could show:
```
Accepted formats: PDF, DOC, DOCX, JPG, PNG
```

## Responsive Design

### Desktop (Default)
- Full width layout
- Button on the right
- Files in vertical list

### Mobile
```
┌────────────────────────────┐
│ Attachments (Optional)     │
│                            │
│ [📤 Add Files]            │
│                            │
│ Upload certificates,       │
│ transcripts, or docs       │
├────────────────────────────┤
│ 📄 cert.pdf       [×]     │
│ (124.5 KB)                 │
├────────────────────────────┤
│ 📄 transcript.pdf [×]     │
│ (89.2 KB)                  │
└────────────────────────────┘
```

## Interactions

1. **Click "Add Files"** → Opens file picker dialog
2. **Select files** → Files upload immediately
3. **Upload completes** → Files appear in list
4. **Click [×]** → Removes file from list
5. **Click file name** (existing) → Opens file in new tab
6. **Click "Save"** → Submits form with attachment IDs

## Accessibility

- File input has `aria-label="Upload attachment files"`
- Button text clearly indicates action
- Error messages are clearly visible
- File names are readable by screen readers
- Remove buttons have clear purpose
