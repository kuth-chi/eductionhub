# Education Form - Attachment Handling Implementation

## Current Status

✅ **Backend:** Attachments are already optional
✅ **Frontend Schema:** `attachment_ids` is already optional
✅ **Frontend UI:** File upload field COMPLETED and added to the form
✅ **File Upload Service:** Extended to support document/attachment uploads

## Backend Implementation

### Serializer (Already Configured)

**File:** `api/serializers/user/resume.py`

```python
class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education history entries"""

    institution = SchoolSerializer(read_only=True)
    institution_uuid = serializers.UUIDField(
        write_only=True, required=False, allow_null=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,  # ✅ Already optional
    )

    def create(self, validated_data):
        # ... existing code ...
        attachments = validated_data.pop("attachments", [])  # ✅ Optional handling
        education = Education.objects.create(**validated_data)
        
        if attachments:  # ✅ Only sets if provided
            education.attachments.set(attachments)
        
        return education

    def update(self, instance, validated_data):
        # ... existing code ...
        attachments = validated_data.pop("attachments", None)  # ✅ Optional handling
        
        if attachments is not None:  # ✅ Only updates if provided
            instance.attachments.set(attachments)
        
        return instance
```

### Model (Already Configured)

**File:** `user/models/base.py`

```python
class Education(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    institution = models.ForeignKey(School, null=True, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100, blank=True, verbose_name=_("degree"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"))
    description = models.TextField(verbose_name=_("description"))
    attachments = models.ManyToManyField(
        "Attachment", 
        blank=True,  # ✅ Already optional
        verbose_name=_("attachments")
    )
```

## Frontend Implementation

### Schema (Already Configured)

**File:** `src/modules/resume/schemas.ts`

```typescript
export const educationInputSchema = z.object({
  institution_uuid: z.string().uuid().optional(),
  degree: z.string().min(1, "Degree is required").max(100, "Degree too long"),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date format (YYYY-MM-DD)"),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date format (YYYY-MM-DD)"),
  description: z.string().min(1, "Description is required"),
  attachment_ids: z.array(z.number()).optional(),  // ✅ Already optional
});
```

### Form Component (✅ COMPLETED)

**File:** `src/modules/resume/ui/components/education-form.tsx`

**Status:** ✅ File upload functionality fully implemented with:
1. ✅ File upload input (hidden, accessed via button)
2. ✅ File upload handler (async with error handling)
3. ✅ Display uploaded files (with file name and size)
4. ✅ Remove file functionality
5. ✅ Show existing attachments when editing
6. ✅ Upload progress indicator
7. ✅ Error message display
8. ✅ Accept multiple file types (.pdf, .doc, .docx, .jpg, .jpeg, .png)

## Recommended Implementation

### Option 1: Add File Upload During Creation/Edit

Add a file upload section to the education form that allows users to:
- Upload files while creating education entry
- Upload files while editing education entry
- Remove uploaded files
- See list of attached files

### Option 2: Separate Attachment Management

Create a separate attachment management interface:
- Users can add education without attachments
- After saving, users can manage attachments via a separate section
- Allows adding/removing attachments anytime

### Option 3: Hybrid Approach (Recommended)

Combine both approaches:
- Allow optional file upload during creation (collapsed/expandable section)
- Provide attachment management after creation
- Best of both worlds - convenience + flexibility

## Implementation Steps

### Step 1: Add File Upload to Education Form

```tsx
// education-form.tsx additions:

// 1. Add state for file handling
const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
const [uploadedAttachmentIds, setUploadedAttachmentIds] = useState<number[]>([]);

// 2. Add file upload handler
const handleFileSelect = async (files: FileList | null) => {
  if (!files) return;
  
  // Upload files to server
  const attachmentIds = await uploadAttachments(Array.from(files));
  setUploadedAttachmentIds(prev => [...prev, ...attachmentIds]);
};

// 3. Add to form submission
const handleSubmit = (data: EducationInput) => {
  const submitData = {
    ...data,
    attachment_ids: uploadedAttachmentIds.length > 0 ? uploadedAttachmentIds : undefined,
  };
  onSubmit(submitData);
};

// 4. Add file upload UI
<FormItem>
  <FormLabel>Attachments (Optional)</FormLabel>
  <FormControl>
    <Input
      type="file"
      multiple
      onChange={(e) => handleFileSelect(e.target.files)}
    />
  </FormControl>
  <FormDescription>
    Upload certificates, transcripts, or other documents (optional)
  </FormDescription>
</FormItem>
```

### Step 2: Create File Upload Service

```typescript
// src/lib/file-upload.ts

export async function uploadAttachments(files: File[]): Promise<number[]> {
  const attachmentIds: number[] = [];
  
  for (const file of files) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);
    
    const response = await authFetch('/api/v1/upload-file/', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    attachmentIds.push(data.id);
  }
  
  return attachmentIds;
}
```

### Step 3: Display Attachments in Education Section

```tsx
// education-section.tsx - Already has this logic
{edu.attachments && edu.attachments.length > 0 && (
  <div className="mt-3">
    <h5 className="font-medium text-sm mb-2">Attachments:</h5>
    {edu.attachments.map((attachment) => (
      <a
        key={attachment.id}
        href={attachment.file_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-primary hover:underline block"
      >
        📎 {attachment.name}
      </a>
    ))}
  </div>
)}
```

## User Workflows

### Workflow 1: Add Education Without Attachments

1. User opens "Add Education" form
2. User fills required fields (degree, dates, description)
3. User skips file upload section (optional)
4. User clicks "Save"
5. ✅ Education saved successfully without attachments

### Workflow 2: Add Education With Attachments

1. User opens "Add Education" form
2. User fills required fields
3. User clicks "Choose Files" and selects documents
4. Files are uploaded and attachment IDs are captured
5. User clicks "Save"
6. ✅ Education saved with attachments

### Workflow 3: Add Attachments Later (Edit)

1. User has existing education entry
2. User clicks "Edit" button
3. Form shows current attachments (if any)
4. User can add more files or remove existing ones
5. User clicks "Save"
6. ✅ Attachments updated

## API Endpoints Needed

### Upload File Endpoint

```
POST /api/v1/upload-file/
Content-Type: multipart/form-data

Body:
- file: File (binary)
- name: string (optional)

Response:
{
  "id": 123,
  "file": "/media/attachments/document.pdf",
  "file_url": "http://localhost:8000/media/attachments/document.pdf",
  "name": "document.pdf",
  "uploaded_at": "2025-10-14T10:30:00Z",
  "content_type": "application/pdf"
}
```

### Create Education with Attachments

```
POST /api/v1/resume/education/
Content-Type: application/json

Body:
{
  "degree": "Bachelor of Science",
  "institution_uuid": "uuid-here",
  "start_date": "2020-01-01",
  "end_date": "2024-06-30",
  "description": "Computer Science program...",
  "attachment_ids": [123, 124]  // Optional
}
```

### Update Education Attachments

```
PATCH /api/v1/resume/education/{id}/
Content-Type: application/json

Body:
{
  "attachment_ids": [123, 124, 125]  // Replaces existing attachments
}
```

## Benefits of This Approach

✅ **Flexibility:** Users can add education quickly without attachments
✅ **Optional:** Attachments are not required, reducing friction
✅ **Editable:** Users can add/remove attachments anytime
✅ **Progressive:** Users can come back later to add documents
✅ **Backend Ready:** Serializer already handles optional attachments
✅ **No Breaking Changes:** Existing functionality remains intact

## Testing Checklist

- [ ] Create education without attachments → Success
- [ ] Create education with attachments → Success
- [ ] Edit education to add attachments → Success
- [ ] Edit education to remove attachments → Success
- [ ] View education with attachments → Displays correctly
- [ ] Download attachment from education → Works
- [ ] Multiple file upload → All files uploaded
- [ ] File type validation → Only allowed types accepted
- [ ] File size validation → Within limits

## Summary

**Current State:**
- ✅ Backend fully supports optional attachments
- ✅ Frontend schema allows optional attachments
- ⚠️ Frontend form UI needs file upload component

**Next Steps:**
1. Add file upload input to education-form.tsx
2. Implement file upload handler
3. Display uploaded files in the form
4. Show attachments in education section (already done)
5. Test all workflows

The foundation is already in place - we just need to add the UI components for file selection and upload! 🎉
